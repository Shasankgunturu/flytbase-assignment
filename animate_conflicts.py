import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

WAYPOINTS_DIR = "waypoints"
FRAME_INTERVAL_MS = 300

def read_waypoints_with_time(filepath):
    waypoints = []
    with open(filepath, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z']) if 'z' in row else 0.0
            timestamp = datetime.fromisoformat(row['timestamp'])
            waypoints.append((x, y, z, timestamp))
    return waypoints


def animate_with_conflicts(conflicts, drone_paths):
    times = sorted(set(pt[3] for traj in drone_paths.values() for pt in traj))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Conflict Animation")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    def update(frame):
        ax.clear()
        t = times[frame]
        ax.set_title(f"Conflicts @ {t.time()}")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_zlim(0, 50)

        for drone_id, traj in drone_paths.items():
            points = [(x, y, z) for x, y, z, ts in traj if ts <= t]
            if points:
                xs, ys, zs = zip(*points)
                ax.plot(xs, ys, zs, label=drone_id)

        # Highlight active conflicts
        for c in conflicts:
            conflict_time = datetime.fromisoformat(c['timestamp'])
            if abs((t - conflict_time).total_seconds()) <= 5:
                x, y, z = c['location']
                ax.scatter(x, y, z, color='red', s=80, marker='X', label='Conflict')

        ax.legend()

    ani = FuncAnimation(fig, update, frames=len(times), interval=FRAME_INTERVAL_MS)

    # Save as MP4 (optional)
    ani.save("conflict_animation.mp4", writer="ffmpeg")
    print("✅ Saved animation as conflict_animation.mp4")

    plt.show()


# Example usage
if __name__ == "__main__":
    import json
    from visualize_drones import read_waypoints_with_time

    # Sample paths
    files = [f for f in os.listdir(WAYPOINTS_DIR) if f.endswith(".csv")]
    paths = {os.path.splitext(f)[0]: read_waypoints_with_time(os.path.join(WAYPOINTS_DIR, f)) for f in files}

    # Sample conflicts
    if os.path.exists("./results/conflicts.json"):
        with open("./results/conflicts.json", "r") as f:
            conflict_data = json.load(f)
        animate_with_conflicts(conflict_data, paths)
    else:
        print("❌ No conflicts.json file found. Run conflict detection first and export conflicts.")
