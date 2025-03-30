import os
import argparse
from generate_waypoints import generate_structured_waypoints, generate_simulated_drones
from visualize_drones import visualize_all_drones, visualize_conflicts, read_waypoints_with_time
from deconfliction_checker import DeconflictionChecker

def run_pipeline(generate=False):
    primary_file = "primary_drone.csv"
    num_simulated = 3
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

    print("🧠 Running conflict detection...")
    checker = DeconflictionChecker(
        primary_csv=primary_path,
        simulated_csv_list=sim_paths, 
        spatial_threshold=5.0, 
        temporal_threshold=60.0
    )
    checker.check_conflicts()
    checker.print_summary()

    # Get conflict details and prepare data for visualization
    status, conflict_list = checker.get_status()

    if conflict_list:
        print("❌ Visualizing conflicts with context...")
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

    args = parser.parse_args()
    run_pipeline(generate=args.generate)
