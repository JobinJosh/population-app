import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import folium
import tempfile
import webbrowser

# Initial data
total_capacity = 120000  # Maximum capacity of Poruba
poruba_coordinates = (49.8285, 18.1733)
existing_population = 100000

# Define bounding box for Poruba (adjust as needed)
poruba_bbox = [
    [49.821, 18.160],  # southwest corner [lat, lon]
    [49.835, 18.185]   # northeast corner [lat, lon]
]

# Function to calculate color based on population
def get_color(existing_population):
    if existing_population <= 0.9 * total_capacity:  # Green for up to 90% of capacity
        return 'green'
    elif existing_population <= 0.99 * total_capacity:  # Yellow for up to 99% of capacity
        return 'yellow'
    else:  # Red for over capacity
        return 'red'

# Function to generate and save map
def generate_map(existing_population):
    # Create a folium map centered around Poruba with specified bounding box
    mymap = folium.Map(location=poruba_coordinates, zoom_start=13, prefer_canvas=True, max_bounds=True)
    mymap.fit_bounds(poruba_bbox)  # Fit map to Poruba bounding box

    # Determine color based on population density
    color = get_color(existing_population)

    # Calculate size of marker based on population
    if existing_population > 0:
        # Calculate the radius of the circle marker based on population density
        marker_radius = 2000 * (existing_population / total_capacity)  # Adjust scale as needed
    else:
        marker_radius = 0

    # Add circle marker for population within Poruba area
    folium.CircleMarker(
        poruba_coordinates,
        radius=marker_radius,
        color=None,
        fill_color=color,
        fill_opacity=0.7,
        popup=f'{existing_population} people ({existing_population / total_capacity:.2%} of capacity)',
    ).add_to(mymap)

    # Save the map as HTML to a temporary file
    tmp_map_path = tempfile.NamedTemporaryFile(suffix=".html").name
    mymap.save(tmp_map_path)

    return tmp_map_path

# Initialize Dash app
app = dash.Dash(__name__)

# Dash app layout
app.layout = html.Div([
    html.H1("Poruba Population Map"),
    html.P(id='population-info'),
    html.P("Adjust the number of people:"),
    dcc.Input(
        id='population-input',
        type='number',
        value=existing_population,
        min=0,
        max=total_capacity,
        step=1000,  # Adjust step size as needed
    ),
    html.Button('Update Map', id='submit-button', n_clicks=0),
    html.Iframe(id='map-container', style={'width': '100%', 'height': '600px', 'border': 'none'}),
])

# Callback to update map based on input value
@app.callback(
    [Output('map-container', 'srcDoc'),
     Output('population-info', 'children')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('population-input', 'value')]
)
def update_map(n_clicks, population_value):
    map_path = generate_map(population_value)
    with open(map_path, 'r') as f:
        map_html = f.read()
    population_percentage = population_value / total_capacity
    info_text = f"Current population: {population_value}, Percentage of capacity: {population_percentage:.2%}"
    return map_html, info_text

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=True)

