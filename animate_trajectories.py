import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

WAYPOINTS_DIR = "waypoints"
FRAME_INTERVAL_MS = 300  # Time between frames


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


def collect_all_trajectories():
    files = [f for f in os.listdir(WAYPOINTS_DIR) if f.endswith(".csv")]
    trajectories = {}
    for f in files:
        label = os.path.splitext(f)[0]
        traj = read_waypoints_with_time(os.path.join(WAYPOINTS_DIR, f))
        trajectories[label] = traj
    return trajectories


def get_global_time_range(trajectories):
    timestamps = [pt[3] for traj in trajectories.values() for pt in traj]
    return min(timestamps), max(timestamps)


def animate_trajectories():
    trajectories = collect_all_trajectories()
    min_time, max_time = get_global_time_range(trajectories)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Drone Trajectory Animation")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    handles = {}
    trails = {}

    for label in trajectories:
        line, = ax.plot([], [], [], label=label)
        handles[label] = line
        trails[label] = []

    times = sorted(set(pt[3] for traj in trajectories.values() for pt in traj))

    def update(frame):
        current_time = times[frame]
        ax.clear()
        ax.set_title(f"Drone Trajectory Animation - {current_time.time()}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_zlim(0, 50)

        for label, traj in trajectories.items():
            trail = [(x, y, z) for x, y, z, t in traj if t <= current_time]
            if trail:
                xs, ys, zs = zip(*trail)
                ax.plot(xs, ys, zs, label=label)

        ax.legend()

    ani = FuncAnimation(fig, update, frames=len(times), interval=FRAME_INTERVAL_MS)

    # Uncomment below to save animation as MP4
    # ani.save("drone_animation.mp4", writer="ffmpeg")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    animate_trajectories()
