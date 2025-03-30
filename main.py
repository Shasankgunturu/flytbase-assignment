import os
import argparse, time
from generate_waypoints import generate_structured_waypoints, generate_simulated_drones
from visualize_drones import visualize_all_drones, visualize_conflicts, read_waypoints_with_time
from deconfliction_checker import DeconflictionChecker
from kdtree_conflict_checker import KDTreeConflictChecker
from rtree_conflict_checker import RTreeConflictChecker

def run_pipeline(generate=False, method="brute", num_drones=3):
    primary_file = "primary_drone.csv"
    num_simulated = num_drones
    sim_files = [f"simulated_drone_{i+1}.csv" for i in range(num_simulated)]
    primary_path = os.path.join("waypoints", primary_file)
    sim_paths = [os.path.join("waypoints", f) for f in sim_files]

    if generate:
        print("🚀 Generating drone waypoints...")

        # Generate primary drone
        generate_structured_waypoints(
            path_type="spiral",
            filename=primary_file,
            drone_label="Primary Drone",
            visualize=False
        )

        # Generate simulated drones
        generate_simulated_drones(
            num_drones=num_simulated,
            base_start_time="2025-01-01 10:00:00",
            is_3D=True,
            visualize=False
        )
        print()

    print("📈 Visualizing all drone trajectories (before conflict detection)...")
    visualize_all_drones(folder_path="waypoints", file_list=[primary_file] + sim_files)

    print("🧠 Running conflict detection using:", method.upper())

    if method == "kdtree":
        checker = KDTreeConflictChecker(
            primary_csv=primary_path,
            simulated_csv_list=sim_paths,
            spatial_threshold=5.0,
            temporal_threshold=60.0
        )
    elif method == "rtree":
        checker = RTreeConflictChecker(
            primary_csv=primary_path,
            simulated_csv_list=sim_paths,
            spatial_threshold=5.0,
            temporal_threshold=60.0
        )
    else:
        checker = DeconflictionChecker(
            primary_csv=primary_path,
            simulated_csv_list=sim_paths,
            spatial_threshold=5.0,
            temporal_threshold=60.0
        )

    start_time = time.perf_counter()
    checker.check_conflicts()
    elapsed = time.perf_counter() - start_time
    checker.print_summary()
    print(f"✅ Conflict detection completed in {round(elapsed, 4)} seconds.")

    status, conflict_list = checker.get_status()

    if conflict_list:
        print("\n❌ Visualizing conflicts with context...")
        drone_paths = {
            os.path.splitext(f)[0]: read_waypoints_with_time(os.path.join("waypoints", f))
            for f in [primary_file] + sim_files
        }
        visualize_conflicts(conflict_list, drone_paths)
    else:
        print("✅ No conflicts to visualize.\n")

if __name__ == "__main__":
    os.makedirs("waypoints", exist_ok=True)

    parser = argparse.ArgumentParser(description="UAV Deconfliction Simulation")
    parser.add_argument("--generate", action="store_true", help="Generate new waypoints before running")
    parser.add_argument("--method", type=str, default="brute", choices=["brute", "kdtree", "rtree"],
                        help="Conflict detection method to use")
    parser.add_argument("--num-drones", type=int, default=3,
                        help="Number of simulated drones to generate and check")

    args = parser.parse_args()
    run_pipeline(generate=args.generate, method=args.method, num_drones=args.num_drones)
