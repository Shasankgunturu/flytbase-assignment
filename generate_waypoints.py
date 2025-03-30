import csv
import math
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mpl_toolkits.mplot3d import Axes3D
import random
import os

# Ensure the ./waypoints folder exists
os.makedirs("waypoints", exist_ok=True)

def generate_structured_waypoints(path_type="line", 
                                   filename="primary_drone.csv", 
                                   num_points=20, 
                                   start_time="2025-01-01 10:00:00", 
                                   interval_seconds=10,
                                   is_3D=True,
                                   visualize=False,
                                   drone_label="Primary"):
    """
    Generate and optionally visualize a structured waypoint path.
    """
    filepath = os.path.join("waypoints", filename)
    waypoints = []
    time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    for i in range(num_points):
        t = i / (num_points - 1)
        
        if path_type == "line":
            x = 100 * t
            y = 100 * t
            z = 30 if is_3D else None

        elif path_type == "circle":
            radius = 50
            angle = 2 * math.pi * t
            x = 50 + radius * math.cos(angle)
            y = 50 + radius * math.sin(angle)
            z = 30 if is_3D else None

        elif path_type == "sinusoid":
            x = 100 * t
            y = 20 * math.sin(4 * math.pi * t) + 50
            z = 30 if is_3D else None

        elif path_type == "spiral":
            radius = 10 + 40 * t
            angle = 4 * math.pi * t
            x = 50 + radius * math.cos(angle)
            y = 50 + radius * math.sin(angle)
            z = 10 + 40 * t if is_3D else None

        else:
            raise ValueError("Unsupported path type")

        timestamp = time_obj + timedelta(seconds=i * interval_seconds)
        if is_3D:
            waypoints.append([round(x, 2), round(y, 2), round(z, 2), timestamp])
        else:
            waypoints.append([round(x, 2), round(y, 2), timestamp])

    # Save to CSV
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        headers = ['x', 'y', 'z', 'timestamp'] if is_3D else ['x', 'y', 'timestamp']
        writer.writerow(headers)
        writer.writerows(waypoints)

    print(f"{drone_label} path saved to {filepath}")

    # Visualization
    if visualize:
        xs = [wp[0] for wp in waypoints]
        ys = [wp[1] for wp in waypoints]
        if is_3D:
            zs = [wp[2] for wp in waypoints]
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(xs, ys, zs, marker='o', label=drone_label)
            ax.set_title(f"{drone_label} - {path_type.capitalize()} Path (3D)")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.legend()
        else:
            plt.plot(xs, ys, marker='o', label=drone_label)
            plt.title(f"{drone_label} - {path_type.capitalize()} Path (2D)")
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.legend()
        plt.grid(True)
        plt.show()


def generate_simulated_drones(num_drones=3, 
                               base_start_time="2025-01-01 10:00:00",
                               path_types=None,
                               interval_seconds=10,
                               is_3D=True,
                               visualize=False):
    """
    Generate waypoints for multiple simulated drones with unique path types.
    """
    if path_types is None:
        path_types = ['line', 'circle', 'sinusoid', 'spiral']

    # Shuffle to ensure unique order
    unique_paths = path_types.copy()
    random.shuffle(unique_paths)

    for i in range(num_drones):
        # Use unique path if available, else randomly reuse from pool
        if i < len(unique_paths):
            path_type = unique_paths[i]
        else:
            path_type = random.choice(path_types)  # fallback if more drones than path types

        offset = timedelta(seconds=random.randint(0, 60))
        drone_start_time = (datetime.strptime(base_start_time, "%Y-%m-%d %H:%M:%S") + offset).strftime("%Y-%m-%d %H:%M:%S")
        filename = f"simulated_drone_{i+1}.csv"
        label = f"Sim Drone {i+1}"

        generate_structured_waypoints(path_type=path_type,
                                      filename=filename,
                                      num_points=30,
                                      start_time=drone_start_time,
                                      interval_seconds=interval_seconds,
                                      is_3D=is_3D,
                                      visualize=visualize,
                                      drone_label=label)


# Example usage
# generate_structured_waypoints(path_type="spiral", filename="primary_drone.csv", drone_label="Primary Drone", visualize=True)
# generate_simulated_drones(num_drones=3, visualize=True)
