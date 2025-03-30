import csv
import os
from datetime import datetime
from scipy.spatial import KDTree

class KDTreeConflictChecker:
    def __init__(self, primary_csv, simulated_csv_list, spatial_threshold=5.0, temporal_threshold=60.0):
        self.primary_csv = primary_csv
        self.simulated_csv_list = simulated_csv_list
        self.spatial_threshold = spatial_threshold
        self.temporal_threshold = temporal_threshold
        self.conflicts = []

    def read_waypoints(self, filename):
        points = []
        with open(filename, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                x = float(row['x'])
                y = float(row['y'])
                z = float(row['z']) if 'z' in row else 0.0
                timestamp = datetime.fromisoformat(row['timestamp'])
                points.append((x, y, z, timestamp))
        return points

    def check_conflicts(self):
        # Load primary drone waypoints
        primary_wp = self.read_waypoints(self.primary_csv)
        primary_xyz = [(x, y, z) for x, y, z, _ in primary_wp]
        primary_times = [t for _, _, _, t in primary_wp]

        # Build KDTree
        tree = KDTree(primary_xyz)

        for sim_csv in self.simulated_csv_list:
            sim_wp = self.read_waypoints(sim_csv)

            for x, y, z, sim_time in sim_wp:
                nearby_idxs = tree.query_ball_point([x, y, z], r=self.spatial_threshold)
                for idx in nearby_idxs:
                    primary_time = primary_times[idx]
                    time_diff = abs((sim_time - primary_time).total_seconds())
                    if time_diff <= self.temporal_threshold:
                        self.conflicts.append({
                            "location": (
                                round((x + primary_xyz[idx][0]) / 2, 2),
                                round((y + primary_xyz[idx][1]) / 2, 2),
                                round((z + primary_xyz[idx][2]) / 2, 2)
                            ),
                            "timestamp": sim_time.isoformat(),
                            "distance": round(tree.query([x, y, z])[0], 2),
                            "time_diff": round(time_diff, 2),
                            "conflicting_drone": os.path.basename(sim_csv)
                        })

    def get_status(self):
        return ("clear", []) if not self.conflicts else ("conflict detected", self.conflicts)

    def print_summary(self):
        status, details = self.get_status()
        print(f"\n🛰️ KDTree Conflict Check: {status.upper()}")
        if details:
            for i, conflict in enumerate(details, 1):
                print(f"\n🚨 Conflict #{i}")
                print(f"• Time       : {conflict['timestamp']}")
                print(f"• Location   : {conflict['location']}")
                print(f"• Drone      : {conflict['conflicting_drone']}")
                print(f"• Distance   : {conflict['distance']} meters")
                print(f"• Time Diff  : {conflict['time_diff']} seconds")
        else:
            print("✅ No conflicts detected.\n")


# Example usage
if __name__ == "__main__":
    primary = "waypoints/primary_drone.csv"
    simulated = [
        "waypoints/simulated_drone_1.csv",
        "waypoints/simulated_drone_2.csv",
        "waypoints/simulated_drone_3.csv"
    ]

    checker = KDTreeConflictChecker(primary, simulated, spatial_threshold=5.0, temporal_threshold=60.0)
    checker.check_conflicts()
    checker.print_summary()
