# 🛰️ Drone Conflict Detection System

A Python-based simulation framework for detecting conflicts between a primary drone and multiple simulated drones using various spatial-temporal techniques.

## 📦 Features
- **Waypoint generation** for primary and multiple simulated drones
- **3D trajectory visualization**
- **Conflict detection** using:
  - Brute-force
  - KD-Tree (spatial point proximity)
  - R-Tree (segment-based bounding box intersection)
- **Conflict visualization with context**
- **Benchmarking** between methods
- CLI-based control for generating and testing scenarios

---

## 📁 Folder Structure
```
flytbase/
├── main.py                          # CLI entrypoint
├── generate_waypoints.py           # Waypoint generation logic
├── visualize_drones.py             # Path & conflict visualizations
├── deconfliction_checker.py        # Brute-force method
├── kdtree_conflict_checker.py      # KDTree-based method
├── rtree_conflict_checker.py       # RTree-based method
├── benchmark_methods.py            # Script to compare performance
└── waypoints/                      # Stores generated .csv files
```

---

## 🚀 How to Run
### 1. Generate Waypoints + Run Detection
```bash
python3 main.py --generate --method rtree --num-drones 5
```

### 2. Run Conflict Check on Existing Data
```bash
python3 main.py --method kdtree
```

### 3. Benchmark All Methods
```bash
python3 benchmark_methods.py
```

---

## ⚖️ Comparison of Methods
| Method      | Speed       | Accuracy | Scales Well | Segment Aware |
|-------------|-------------|----------|-------------|----------------|
| Brute Force | ❌ Slow      | ✅ High   | ❌ No        | ✅ Yes         |
| KD-Tree     | ✅ Fast      | ✅ Good   | ✅ Yes       | ❌ No          |
| R-Tree      | ✅✅ Very Fast| ✅✅ High | ✅✅ Yes      | ✅✅ Yes        |

---

## 📊 Output
- Drones plotted in 3D space
- Conflicts marked with red ❌ and nearby points
- Console summary of all detected conflicts with:
  - Timestamp
  - Location
  - Distance
  - Involved drone

---

## 🧰 Requirements
- Python 3.8+
- `matplotlib`, `scipy`, `rtree`, `sklearn`

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 📌 Notes
- All waypoints are saved in `./waypoints` as CSV
- Conflicts are visualized only when they exist
- Time threshold and spatial radius are configurable in each checker class

---

## 🙌 Author
Built by Shasank Gunturu

---

Feel free to extend this framework with:
- Animated trajectories
- More complex airspace logic
- Integration with real-time data
