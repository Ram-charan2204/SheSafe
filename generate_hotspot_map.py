import pandas as pd
import folium
from folium.plugins import HeatMap

# ---------------- LOAD DATA ----------------
df = pd.read_csv("alert_logs.csv")

# ---------------- RISK WEIGHTS ----------------
ALERT_WEIGHTS = {
    "SOS_GESTURE": 5,
    "HIGH_RISK_AUDIO": 4,
    "WOMAN_SURROUNDED": 3,
    "WOMAN_ISOLATED": 1
}

df["risk_score"] = df["alert_type"].map(ALERT_WEIGHTS)

# ---------------- CREATE LOCATION BUCKETS ----------------
# Round lat/lon to group nearby alerts (hotspot clustering)
df["lat_bucket"] = df["latitude"].round(3)
df["lon_bucket"] = df["longitude"].round(3)

# ---------------- AGGREGATE HOTSPOTS ----------------
hotspots = (
    df.groupby(["lat_bucket", "lon_bucket"])
      .agg(
          total_risk=("risk_score", "sum"),
          alert_count=("alert_type", "count")
      )
      .reset_index()
      .sort_values(by="total_risk", ascending=False)
)

# ---------------- PRINT SORTED HOTSPOTS ----------------
print("\n🔥 HOTSPOTS SORTED BY RISK (HIGH → LOW)\n")
print(hotspots)

# Save for UI / report
hotspots.to_csv("hotspot_priority.csv", index=False)

# ---------------- GENERATE MAP ----------------
# Center map at average location
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Heatmap data: [lat, lon, weight]
heat_data = [
    [row["lat_bucket"], row["lon_bucket"], row["total_risk"]]
    for _, row in hotspots.iterrows()
]

HeatMap(heat_data, radius=25).add_to(m)

# Optional: Mark top 5 hotspots
for i, row in hotspots.head(5).iterrows():
    folium.Marker(
        location=[row["lat_bucket"], row["lon_bucket"]],
        popup=f"Risk Score: {row['total_risk']}\nAlerts: {row['alert_count']}",
        icon=folium.Icon(color="red")
    ).add_to(m)

# Save map
m.save("crime_hotspot_map.html")

print("\n✅ Files generated:")
print(" - crime_hotspot_map.html")
print(" - hotspot_priority.csv")
