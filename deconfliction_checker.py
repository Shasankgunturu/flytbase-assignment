import csv
import os
from datetime import datetime
from math import sqrt

class DeconflictionChecker:
    def __init__(self, primary_csv, simulated_csv_list, spatial_threshold=5.0, temporal_threshold=1.0):
        self.primary_csv = primary_csv
        self.simulated_csv_list = simulated_csv_list
        self.spatial_threshold = spatial_threshold
        self.temporal_threshold = temporal_threshold
        self.conflicts = []

    def read_waypoints(self, filename):
        waypoints = []
        with open(filename, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                x = float(row['x'])
                y = float(row['y'])
                z = float(row['z']) if 'z' in row else 0.0
                timestamp = datetime.fromisoformat(row['timestamp'])
                waypoints.append((x, y, z, timestamp))
        return waypoints

    def euclidean_distance(self, p1, p2):
        return sqrt((p1[0] - p2[0])**2 +
                    (p1[1] - p2[1])**2 +
                    (p1[2] - p2[2])**2)

    def check_conflicts(self):
        primary_wp = self.read_waypoints(self.primary_csv)
        for sim_csv in self.simulated_csv_list:
            sim_wp = self.read_waypoints(sim_csv)
            for p1 in primary_wp:
                for p2 in sim_wp:
                    time_diff = abs((p1[3] - p2[3]).total_seconds())
                    if time_diff <= self.temporal_threshold:
                        distance = self.euclidean_distance(p1, p2)
                        if distance <= self.spatial_threshold:
                            self.conflicts.append({
                                "location": (round((p1[0]+p2[0])/2, 2),
                                             round((p1[1]+p2[1])/2, 2),
                                             round((p1[2]+p2[2])/2, 2)),
                                "timestamp": p1[3].isoformat(),
                                "distance": round(distance, 2),
                                "time_diff": round(time_diff, 2),
                                "conflicting_drone": os.path.basename(sim_csv)
                            })

    def get_status(self):
        return ("clear", []) if not self.conflicts else ("conflict detected", self.conflicts)

    def print_summary(self):
        status, details = self.get_status()
        print(f"\n🛰️ Mission Status: {status.upper()}")
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

# # 🔽 Example usage
# if __name__ == "__main__":
#     folder = "./waypoints"
#     primary = os.path.join(folder, "primary_drone.csv")
    
#     # Dynamically collect all simulated drones
#     simulated = [
#         os.path.join(folder, f) for f in os.listdir(folder)
#         if f.startswith("simulated_drone_") and f.endswith(".csv")
#     ]

#     checker = DeconflictionChecker(primary, simulated, spatial_threshold=5.0, temporal_threshold=60.0)
#     checker.check_conflicts()
#     checker.print_summary()
