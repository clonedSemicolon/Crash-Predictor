import pandas as pd
import numpy as np
import folium
from sklearn.cluster import MiniBatchKMeans


traffic_crash = pd.read_csv('/content/drive/MyDrive/location_cause_dataset.csv',low_memory=False)
df = traffic_crash.dropna(subset=['LATITUDE', 'LONGITUDE'])

LAT_BIN_SIZE = 0.0145
LON_BIN_SIZE = 0.018

# Binning coordinates
df["lat_bin"] = (df["LATITUDE"] // LAT_BIN_SIZE) * LAT_BIN_SIZE
df["lon_bin"] = (df["LONGITUDE"] // LON_BIN_SIZE) * LON_BIN_SIZE

# Group and count crashes
heatmap_data = df.groupby(["lat_bin", "lon_bin"]).size().reset_index(name="crash_count")

# Normalize values for radius and color scaling
max_count = heatmap_data["crash_count"].max()
min_count = heatmap_data["crash_count"].min()

# Function to get color based on crash count
def get_color(count):
    if count > 0.75 * max_count:
        return "red"
    elif count > 0.4 * max_count:
        return "orange"
    else:
        return "green"

# Function to scale radius
def get_radius(count):
    # base radius: 1000m to 4000m
    return 1000 + (3000 * (count - min_count) / (max_count - min_count))

# Create map
map_center = [41.8781, -87.6298]
m = folium.Map(location=map_center, zoom_start=12,
    tiles="CartoDB dark_matter")

marker_cluster = MarkerCluster().add_to(m)

for _, row in heatmap_data.iterrows():
    lat = row['lat_bin'] + LAT_BIN_SIZE / 2
    lon = row['lon_bin'] + LON_BIN_SIZE / 2
    count = row["crash_count"]

    folium.Marker(
        location=(lat, lon),
        popup=f"Crashes: {count}"
    ).add_to(marker_cluster)


# Save map
m.save("/content/drive/My Drive/chicago_crash_map_2.html")
print("✅ Map saved as 'chicago_crash_map.html'")
