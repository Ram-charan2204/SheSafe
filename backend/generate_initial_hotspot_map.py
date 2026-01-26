import folium
from camera_config import CAMERAS

def generate_initial_hotspot_map():
    # Default center (average of camera locations)
    avg_lat = sum(c["lat"] for c in CAMERAS) / len(CAMERAS)
    avg_lon = sum(c["lon"] for c in CAMERAS) / len(CAMERAS)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for cam in CAMERAS:
        folium.CircleMarker(
            location=[cam["lat"], cam["lon"]],
            radius=8,
            popup=f"{cam['id']} | Risk: 0",
            color="green",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    m.save("crime_hotspot_map.html")
