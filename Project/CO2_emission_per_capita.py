import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

# Step 1: Read the dataset
df = pd.read_csv("co-emissions-per-capita.csv")

# Step 2: Filter data for year 2022
df_2022 = df[df['Year'] == 2022].copy()  # Make a copy to avoid SettingWithCopyWarning

# Round the "Annual CO₂ Emissions per Capita (2022)" to 1 decimal place using .loc indexer
df_2022.loc[:, "Annual CO₂ emissions (per capita)"] = df_2022["Annual CO₂ emissions (per capita)"].round(1)

# Step 3: Create a Plotly Dash app
app = Dash(__name__)

# app.layout = html.Div([
#     html.Div([
#         dcc.Graph(id="map-graph", style={'height': '100vh'}),  # Adjust height of the map
#     ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-bottom': '10px'}),  # Adjust margin-bottom
#     html.Div([
#         html.Div(id="mini-graph-heading", style={'text-align': 'center', 'font-size': '16px'}),  # Align text to center
#         html.Div(id="mini-graph-container", style={'text-align': 'center'})  # Align the container to center
#     ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})  # Adjust margin-bottom
# ])

app.layout = html.Div([
    html.Div([
        dcc.Graph(id="map-graph", style={'height': '80vh'}),  # Adjust height of the map
        html.Div(id="mini-graph-heading", style={'text-align': 'center', 'font-size': '16px'}),  # Align text to center
        html.Div(id="mini-graph-container", style={'text-align': 'center'})  # Align the container to center
    ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-bottom': '10px'})  # Adjust margin-bottom
])

@app.callback(
    Output("map-graph", "figure"),
    Output("mini-graph-heading", "children"),
    Output("mini-graph-container", "children"),
    Input("map-graph", "hoverData")
)
def update_map(hoverData):
    # Create the world map
    fig = px.choropleth(
        df_2022,
        locations="Entity",
        locationmode="country names",
        color="Annual CO₂ emissions (per capita)",
        projection="natural earth",
        hover_name="Entity",
        hover_data={"Entity":False ,"Annual CO₂ emissions (per capita)": True},  # Remove "Entity" from hover info
        title="Annual CO₂ Emissions per Capita (2022) (in tonnes per person)",
        color_continuous_scale=px.colors.sequential.YlOrBr,  # Change color scale
        range_color=(0, 20),  # Set color range from 0 to 20t
    )

    mini_graph_heading = ""
    mini_graph_div = None

    if hoverData is not None and "points" in hoverData:
        # Extract country name from hoverData
        country_name = hoverData["points"][0]["hovertext"]

        # Step 4: Implement hover functionality
        country_df = df[df["Entity"] == country_name]
        mini_graph = go.Scatter(
            x=country_df["Year"],
            y=country_df["Annual CO₂ emissions (per capita)"],
            mode="lines+markers",
            name="CO₂ emissions trend",
            marker=dict(size=1)  # Adjust the marker size here
        )
        mini_fig = go.Figure(mini_graph)
        mini_fig.update_layout(width=600, height=200, margin=dict(t=10))
        mini_graph_div = dcc.Graph(figure=mini_fig)

        mini_graph_heading = html.H5("CO₂ emissions (per capita) trend - " + country_name)

    return fig, mini_graph_heading, mini_graph_div

if __name__ == "__main__":
    app.run_server(debug=True)
