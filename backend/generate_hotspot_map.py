import pandas as pd
import folium
from folium.plugins import HeatMap

# ---------------- LOAD DATA ----------------
df = pd.read_csv("hotspot_priority.csv")

if df.empty:
    print("⚠️ No hotspot data available.")
    exit()

# ---------------- MAP CENTER ----------------
center_lat = df["lat_bucket"].mean()
center_lon = df["lon_bucket"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# ---------------- HEATMAP (INTENSITY) ----------------
heat_data = [
    [row["lat_bucket"], row["lon_bucket"], row["total_risk"]]
    for _, row in df.iterrows()
]

HeatMap(heat_data, radius=30, blur=20).add_to(m)

# ---------------- RISK COLOR FUNCTION ----------------
def risk_color(risk):
    if risk >= 15:
        return "red"
    elif risk >= 5:
        return "orange"
    return "green"

# ---------------- COLORED HOTSPOTS ----------------
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["lat_bucket"], row["lon_bucket"]],
        radius=10,
        color=risk_color(row["total_risk"]),
        fill=True,
        fill_color=risk_color(row["total_risk"]),
        fill_opacity=0.8,
        popup=(
            f"Risk: {row['total_risk']}<br>"
            f"Alerts: {row['alert_count']}"
        )
    ).add_to(m)

# ---------------- SAVE MAP ----------------
m.save("crime_hotspot_map.html")
print("✅ Hotspot map updated with severity colors")
