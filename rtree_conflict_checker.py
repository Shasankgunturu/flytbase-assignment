import csv
import os
from datetime import datetime
from rtree import index
from math import sqrt

class RTreeConflictChecker:
    def __init__(self, primary_csv, simulated_csv_list, spatial_threshold=5.0, temporal_threshold=60.0):
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

    def build_segment_boxes(self, waypoints):
        boxes = []
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i + 1]

            minx = min(p1[0], p2[0])
            miny = min(p1[1], p2[1])
            minz = min(p1[2], p2[2])
            maxx = max(p1[0], p2[0])
            maxy = max(p1[1], p2[1])
            maxz = max(p1[2], p2[2])

            start_time = min(p1[3], p2[3])
            end_time = max(p1[3], p2[3])

            boxes.append({
                "bbox": (minx, miny, minz, maxx, maxy, maxz),
                "segment": (p1, p2),
                "time_window": (start_time, end_time)
            })
        return boxes

    def distance_between_segments(self, A, B, C, D):
        def dot(u, v): return sum(ux * vx for ux, vx in zip(u, v))
        def norm(v): return sqrt(dot(v, v))
        def sub(u, v): return tuple(ux - vx for ux, vx in zip(u, v))
        def add(u, v): return tuple(ux + vx for ux, vx in zip(u, v))
        def scalar_mult(s, v): return tuple(s * x for x in v)

        u = sub(B, A)
        v = sub(D, C)
        w0 = sub(A, C)

        a = dot(u, u)
        b = dot(u, v)
        c = dot(v, v)
        d = dot(u, w0)
        e = dot(v, w0)

        denom = a * c - b * b
        s = (b * e - c * d) / denom if denom else 0
        t = (a * e - b * d) / denom if denom else 0

        s = max(0, min(1, s))
        t = max(0, min(1, t))

        closest1 = add(A, scalar_mult(s, u))
        closest2 = add(C, scalar_mult(t, v))
        distance = norm(sub(closest1, closest2))
        return distance

    def deduplicate_conflicts(self):
        unique_conflicts = []
        seen = set()

        for conflict in self.conflicts:
            key = (conflict['conflicting_drone'],
                   conflict['location'],
                   round(datetime.fromisoformat(conflict['timestamp']).timestamp()))

            if key not in seen:
                seen.add(key)
                unique_conflicts.append(conflict)

        self.conflicts = unique_conflicts

    def check_conflicts(self):
        primary_wp = self.read_waypoints(self.primary_csv)
        primary_boxes = self.build_segment_boxes(primary_wp)

        p_index = index.Index(properties=index.Property(dimension=3))
        for i, item in enumerate(primary_boxes):
            p_index.insert(i, item["bbox"])

        for sim_csv in self.simulated_csv_list:
            sim_wp = self.read_waypoints(sim_csv)
            sim_boxes = self.build_segment_boxes(sim_wp)

            for sim_item in sim_boxes:
                sim_bbox = sim_item["bbox"]
                sim_seg = sim_item["segment"]
                sim_time_window = sim_item["time_window"]

                matches = list(p_index.intersection(sim_bbox))

                for match_idx in matches:
                    p_seg = primary_boxes[match_idx]["segment"]
                    p_time_window = primary_boxes[match_idx]["time_window"]

                    mid_sim = sim_time_window[0] + (sim_time_window[1] - sim_time_window[0]) / 2
                    mid_primary = p_time_window[0] + (p_time_window[1] - p_time_window[0]) / 2
                    time_diff = abs((mid_sim - mid_primary).total_seconds())

                    if time_diff <= self.temporal_threshold:
                        dist = self.distance_between_segments(
                            sim_seg[0][:3], sim_seg[1][:3],
                            p_seg[0][:3], p_seg[1][:3]
                        )

                        if dist <= self.spatial_threshold:
                            self.conflicts.append({
                                "location": (
                                    round((sim_seg[0][0] + sim_seg[1][0]) / 2, 2),
                                    round((sim_seg[0][1] + sim_seg[1][1]) / 2, 2),
                                    round((sim_seg[0][2] + sim_seg[1][2]) / 2, 2),
                                ),
                                "timestamp": mid_sim.isoformat(),
                                "distance": round(dist, 2),
                                "time_diff": round(time_diff, 2),
                                "conflicting_drone": os.path.basename(sim_csv)
                            })
        self.deduplicate_conflicts()

    def get_status(self):
        return ("clear", []) if not self.conflicts else ("conflict detected", self.conflicts)

    def print_summary(self):
        status, details = self.get_status()
        print(f"\n📦 R-Tree Conflict Check: {status.upper()}")
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