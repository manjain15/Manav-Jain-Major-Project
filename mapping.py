import folium
from folium import plugins

# Set coordinates (latitude, longitude)
coordinates = [(-33.734252, 150.963677), (-33.730301, 150.944148), (-33.712323, 150.934008)]  # Norwest Station to Kellyville Station

# Create a map centered at the mean latitude and longitude of the coordinates
map_center = [sum(coord[0] for coord in coordinates) / len(coordinates),
              sum(coord[1] for coord in coordinates) / len(coordinates)]

# Create the map
m = folium.Map(location=map_center, zoom_start=4)

# Add markers for each coordinate
for coord in coordinates:
    folium.Marker(location=coord).add_to(m)

# Create an AntPath to represent the transport route
ant_path = plugins.AntPath(locations=coordinates, color='blue')
m.add_child(ant_path)

# Save the map to an HTML file
m.save('map_with_coordinates.html')
