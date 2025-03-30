import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime

def read_waypoints(filename):
    waypoints = []
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z']) if 'z' in row else None
            waypoints.append((x, y, z))
    return waypoints

def read_waypoints_with_time(filename):
    waypoints = []
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z']) if 'z' in row else None
            timestamp = datetime.fromisoformat(row['timestamp'])
            waypoints.append((x, y, z, timestamp))
    return waypoints

def visualize_all_drones(folder_path="./waypoints", file_list=None):
    if file_list is None:
        file_list = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.endswith(".csv")
        ]
    else:
        file_list = [os.path.join(folder_path, f) for f in file_list]

    fig = plt.figure()
    is_3D = None
    ax = None

    for filepath in file_list:
        waypoints = read_waypoints(filepath)
        xs = [pt[0] for pt in waypoints]
        ys = [pt[1] for pt in waypoints]
        zs = [pt[2] for pt in waypoints if pt[2] is not None]

        label = os.path.splitext(os.path.basename(filepath))[0]

        if is_3D is None:
            is_3D = zs and len(zs) == len(xs)
            ax = fig.add_subplot(111, projection='3d') if is_3D else fig.add_subplot(111)

        if is_3D:
            ax.plot(xs, ys, zs, marker='o', label=label)
        else:
            ax.plot(xs, ys, marker='o', label=label)

    ax.set_title("Drone Trajectories")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    if is_3D:
        ax.set_zlabel("Z")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def visualize_conflicts(conflicts, drone_paths):
    fig = plt.figure()
    is_3D = None
    ax = None

    # Plot all drone paths again
    for drone_id, waypoints in drone_paths.items():
        xs = [pt[0] for pt in waypoints]
        ys = [pt[1] for pt in waypoints]
        zs = [pt[2] for pt in waypoints if pt[2] is not None]

        if is_3D is None:
            is_3D = zs and len(zs) == len(xs)
            ax = fig.add_subplot(111, projection='3d') if is_3D else fig.add_subplot(111)

        if is_3D:
            ax.plot(xs, ys, zs, marker='o', label=drone_id)
        else:
            ax.plot(xs, ys, marker='o', label=drone_id)

    # Plot conflicts with context
    for conflict in conflicts:
        x, y, z = conflict['location']
        timestamp = datetime.fromisoformat(conflict['timestamp'])
        label = f"{conflict['conflicting_drone']} @ {timestamp.time()}"

        if is_3D:
            ax.scatter(x, y, z, color='red', s=80, marker='X', label=f"Conflict: {label}")
        else:
            ax.scatter(x, y, color='red', s=80, marker='X', label=f"Conflict: {label}")

        # Plot nearby points for both drones
        for drone_id in ['primary_drone', os.path.splitext(conflict['conflicting_drone'])[0]]:
            if drone_id not in drone_paths:
                continue

            waypoints = drone_paths[drone_id]
            indices = [i for i, pt in enumerate(waypoints) if abs((pt[3] - timestamp).total_seconds()) < 0.01]
            if not indices:
                continue

            idx = indices[0]
            nearby = waypoints[max(0, idx-1):min(len(waypoints), idx+2)]
            xs = [pt[0] for pt in nearby]
            ys = [pt[1] for pt in nearby]
            zs = [pt[2] for pt in nearby if pt[2] is not None]

            if is_3D:
                ax.plot(xs, ys, zs, linestyle='dotted', color='gray')
                ax.scatter(xs, ys, zs, color='black', s=30, marker='o')
            else:
                ax.plot(xs, ys, linestyle='dotted', color='gray')
                ax.scatter(xs, ys, color='black', s=30, marker='o')

    ax.set_title("Conflict Visualization")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    if is_3D:
        ax.set_zlabel("Z")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

