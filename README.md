# UAV Deconfliction Simulation 🛩️

This project simulates autonomous drone flight paths, detects potential conflicts (spatial & temporal), and visualizes both trajectories and conflict zones.

---

## 📁 Project Structure

```
.
├── main.py
├── generate_waypoints.py
├── visualize_drones.py
├── deconfliction_checker.py
├── waypoints/                # Stores all generated .csv files
├── README.md
└── reflection.pdf            # Design + explanation document (separate)
```

---

## 🚀 Features

- Generate structured waypoint paths (line, spiral, circle, sinusoid)
- Simulated drones follow different paths
- Time-stamped CSV waypoints
- Detects conflicts based on spatial & temporal proximity
- Visualizes:
  - Drone trajectories (2D/3D)
  - Conflict points with nearby path segments
- CLI flag to control generation step

---

## 🛠️ Requirements

- Python 3.x
- `matplotlib`

Install dependencies:
```bash
pip install matplotlib
```

---

## 🧩 How to Run

### 1. Generate Waypoints + Visualize + Detect Conflicts:
```bash
python main.py --generate
```

### 2. Only Visualize & Detect using existing CSVs:
```bash
python main.py
```

---

## 📈 Outputs

- `waypoints/*.csv` → Drone path data
- Visual plot:
  - All drone trajectories
  - Conflict points (red `X`)
  - Pre/post conflict waypoints (gray dots, dotted lines)
- Console summary of each conflict:
  - Time
  - Location
  - Distance
  - Conflicting drone

---

## 📌 Conflict Detection Logic

- **Spatial threshold**: 5.0 meters
- **Temporal threshold**: 60 seconds
- Conflict occurs if:
  ```python
  distance < threshold AND |t1 - t2| < threshold
  ```

---

## 📚 File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Central pipeline with optional CLI flag (`--generate`) |
| `generate_waypoints.py` | Creates waypoints for primary and simulated drones |
| `visualize_drones.py` | Visualizes trajectories and conflict zones |
| `deconfliction_checker.py` | Class that detects and logs conflicts |
| `waypoints/` | Stores `.csv` files for each drone's path |
| `README.md` | This guide |
| `reflection.pdf` | Design justification and scalability discussion |

---

## ✅ Sample Output

```
🛰️ Mission Status: CONFLICT DETECTED

🚨 Conflict #1
• Time       : 2025-01-01T10:01:10
• Location   : (48.7, 51.2, 29.3)
• Drone      : simulated_drone_2.csv
• Distance   : 3.92 meters
• Time Diff  : 0.00 seconds
```

---

## 🧠 Notes

- Drone paths are generated using math-based parametric functions
- Waypoints include timestamps to simulate real-world flight scheduling
- Simulated drones are randomly offset in start time to test conflicts
- Modular architecture makes it easy to expand

---

## 👨‍💻 Authors

- Your Name(s)
- [GitHub or email if applicable]

---

## 📎 License

MIT (or as per your institution's rules)