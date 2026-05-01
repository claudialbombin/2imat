# generate_maps.py
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import argparse

city_coordinates = {
    'Manchester': (53.4808, -2.2426),
    'WashingtonDC': (38.9072, -77.0369),
    'Glasgow': (55.8642, -4.2518),
    'ElPaso': (31.7619, -106.4850)
}

def plot_and_save_map(filtered_file_path: str, city_name: str, output_html_path: str):
    """Crea un mapa con los check-ins."""
    try:
        data = pd.read_csv(filtered_file_path, delimiter='\t', header=None,
                          names=['user', 'check-in_time', 'latitude', 'longitude', 'location_id'])
        
        if city_name not in city_coordinates:
            raise ValueError(f"City '{city_name}' not found.")
        
        city_lat, city_lon = city_coordinates[city_name]
        
        map_ = folium.Map(location=[city_lat, city_lon], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(map_)
        
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"User: {row['user']}<br>Time: {row['check-in_time']}"
            ).add_to(marker_cluster)
        
        map_.save(output_html_path)
        print(f"Map saved to {output_html_path}")
        
    except Exception as e:
        print(f"Error generating map: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate map from check-in data.")
    parser.add_argument("--input_file", required=True, help="Path to input file")
    parser.add_argument("--city_name", required=True, help="City name")
    parser.add_argument("--output_html", required=True, help="Output HTML file path")
    
    args = parser.parse_args()
    plot_and_save_map(args.input_file, args.city_name, args.output_html)

if __name__ == "__main__":
    main()