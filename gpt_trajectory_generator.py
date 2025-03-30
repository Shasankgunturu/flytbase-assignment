import os
import csv
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_gpt_waypoints(prompt, output_filename):
    print(f"🧠 Asking GPT for: {output_filename}...")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant generating drone flight waypoints."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    text = response.choices[0].message.content.strip()
    lines = [line for line in text.split('\n') if ',' in line]

    waypoints = []
    for line in lines:
        try:
            x, y, z, t = [p.strip() for p in line.split(',')]
            waypoints.append([float(x), float(y), float(z), datetime.fromisoformat(t)])
        except:
            continue

    if not waypoints:
        print("⚠️ No valid waypoints parsed.")
        return

    os.makedirs("waypoints", exist_ok=True)
    path = os.path.join("waypoints", output_filename)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'z', 'timestamp'])
        writer.writerows([[x, y, z, t.isoformat()] for x, y, z, t in waypoints])

    print(f"✅ Saved to {path}")

# Example
if __name__ == "__main__":
    prompt = (
        "Generate 25 natural 3D waypoints for a drone flying manually in an open area. "
        "Include gentle curves, ascents, and descents. Start at (0, 0, 10). "
        "Waypoints should be 5 seconds apart starting at 2025-01-01T10:00:00. "
        "Format each line as: x, y, z, timestamp (ISO 8601)."
    )
    generate_gpt_waypoints(prompt, "primary_drone.csv")
