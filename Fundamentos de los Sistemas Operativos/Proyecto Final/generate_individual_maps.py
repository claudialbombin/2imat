# generate_individual_maps.py
import argparse
import pandas as pd
from datetime import datetime
import folium
from folium.plugins import AntPath

# Coordinates of the cities
city_coordinates = {
    'Manchester': (53.4808, -2.2426),
    'WashingtonDC': (38.9072, -77.0369),
    'Glasgow': (55.8642, -4.2518),
    'ElPaso': (31.7619, -106.4850)
}


def parse_args():
    """
    Parse the command line arguments.

    Returns:
        args: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate a map showing a user's route through Points of Interest in a city."
    )
    parser.add_argument("--user_id", type=int, required=True, help="User ID")
    parser.add_argument("--city_name", type=str, required=True, help="City name")
    parser.add_argument("--input_file", type=str, required=True, help="Input file containing check-ins")
    parser.add_argument("--output_html", type=str, required=True, help="Output HTML file")
    return parser.parse_args()


def generate_route(user_id, city_name, input_file, output_html):
    """
    Generate a map showing the route of a specific user through Points of Interest.

    Args:
        user_id (int): The ID of the user.
        city_name (str): The name of the city.
        input_file (str): Path to the input file with check-ins data.
        output_html (str): Path to the output HTML file where the map will be saved.

    Raises:
        ValueError: If the city name is not found in the predefined coordinates.
    """
    # Read the check-ins data
    data = pd.read_csv(input_file, delimiter='\t', header=None)
    data.columns = ['user_id', 'timestamp', 'latitude', 'longitude', 'poi_id']

    # Filter the data for the specified user
    user_data = data[data['user_id'] == user_id]

    # If the user does not exist in the data, exit the function
    if user_data.empty:
        print(f"User ID {user_id} not found in the data. No file will be generated.")
        return

    # Convert the timestamp column to datetime format, accounting for the "Z" suffix
    user_data.loc[:, 'timestamp'] = pd.to_datetime(user_data['timestamp'], format='%Y-%m-%dT%H:%M:%SZ')

    # Sort the data by timestamp
    user_data = user_data.sort_values('timestamp')

    # Get the coordinates for the specified city
    city_center = city_coordinates.get(city_name)
    if not city_center:
        raise ValueError(f"Coordinates for the city {city_name} are not defined.")

    # Create a map centered on the specified city
    m = folium.Map(location=city_center, zoom_start=12)

    # Add markers and paths to the map
    coords = user_data[['latitude', 'longitude']].values.tolist()
    for idx, (lat, lon) in enumerate(coords, start=1):
        folium.Marker(
            location=[lat, lon],
            popup=f"Order: {idx}<br>Latitude: {lat}<br>Longitude: {lon}",
            icon=folium.DivIcon(html=f"""<div style="font-family: sans-serif; color: blue">{idx}</div>""")
        ).add_to(m)

    # Add the route path to the map
    if len(coords) > 1:
        AntPath(locations=coords, color="blue", weight=5, dash_array=[10, 20]).add_to(m)

    # Save the map to the output HTML file
    m.save(output_html)
    print(f"Map saved to {output_html}")


if __name__ == "__main__":
    args = parse_args()
    generate_route(args.user_id, args.city_name, args.input_file, args.output_html)
