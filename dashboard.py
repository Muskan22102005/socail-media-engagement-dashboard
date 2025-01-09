import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load the dataset
data = pd.read_csv("C:\\Users\\sonam\\OneDrive\\Desktop\\praveen sona\\social_media_engagement.csv")
data['Date'] = pd.to_datetime(data['Date'])  # Ensure the Date column is in datetime format

# Initialize the Dash app
app = Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    # Header with icons
    html.Div([
        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/8/89/Facebook_Logo_%282019%29.svg", 
                 style={'height': '40px', 'margin-right': '20px'}),
        html.H1(
            "Social Media Engagement Dashboard",
            style={'text-align': 'center', 'color': '#ffffff', 'flex': '1', 'margin': '0'}
        ),
        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png", 
                 style={'height': '40px', 'margin-left': '20px'}),
    ], style={
        'background-color': '#003366',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'space-between',
        'padding': '20px',
        'border-radius': '8px',
        'margin-bottom': '20px'
    }),
    
    # Filters
    html.Div([
        html.Div([
            html.Label("Select Platform:", style={'color': '#003366'}),
            dcc.Dropdown(
                id="platform-filter",
                options=[{"label": platform, "value": platform} for platform in data['Platform'].unique()],
                value=None,
                placeholder="All Platforms",
                multi=True,
                style={'margin-bottom': '15px'}
            ),
            html.Label("Select Content Type:", style={'color': '#003366'}),
            dcc.Dropdown(
                id="content-filter",
                options=[{"label": content, "value": content} for content in data['Content_Type'].unique()],
                value=None,
                placeholder="All Content Types",
                multi=True,
                style={'margin-bottom': '15px'}
            ),
            html.Label("Select Action:", style={'color': '#003366'}),
            dcc.Dropdown(
                id="action-filter",
                options=[{"label": action, "value": action} for action in data['Action'].unique()],
                value=None,
                placeholder="All Actions",
                multi=True,
                style={'margin-bottom': '15px'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '15px', 'background': '#f9f9f9', 'border-radius': '8px'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding-bottom': '20px'}),

    # Graphs
    html.Div([
        html.Div([dcc.Graph(id="time-series-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([dcc.Graph(id="bar-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    html.Div([
        html.Div([dcc.Graph(id="pie-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([dcc.Graph(id="histogram-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # New Violin and Heatmap charts
    html.Div([
        html.Div([dcc.Graph(id="violin-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([dcc.Graph(id="heatmap-chart")], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

], style={'background-color': '#f0f0f5', 'padding': '20px', 'border-radius': '10px'})

# Callbacks to update the visualizations based on filters
@app.callback(
    [Output("time-series-chart", "figure"),
     Output("bar-chart", "figure"),
     Output("pie-chart", "figure"),
     Output("histogram-chart", "figure"),
     Output("violin-chart", "figure"),
     Output("heatmap-chart", "figure")],
    [Input("platform-filter", "value"),
     Input("content-filter", "value"),
     Input("action-filter", "value")]
)
def update_charts(selected_platforms, selected_content, selected_actions):
    # Filter the data based on selections
    filtered_data = data.copy()
    if selected_platforms:
        filtered_data = filtered_data[filtered_data['Platform'].isin(selected_platforms)]
    if selected_content:
        filtered_data = filtered_data[filtered_data['Content_Type'].isin(selected_content)]
    if selected_actions:
        filtered_data = filtered_data[filtered_data['Action'].isin(selected_actions)]

    # Handle empty data gracefully
    if filtered_data.empty:
        return (
            px.line(title="No Data Available"),
            px.bar(title="No Data Available"),
            px.pie(title="No Data Available"),
            px.histogram(title="No Data Available"),
            px.violin(title="No Data Available"),
            px.density_heatmap(title="No Data Available")
        )

    # Time-series chart
    time_series_fig = px.line(
        filtered_data.groupby(['Date']).sum().reset_index(),
        x="Date",
        y="Engagement_Count",
        title="Engagement Trend Over Time",
        labels={"Engagement_Count": "Engagements", "Date": "Date"}
    )

    # Bar chart: Top 10 posts by engagement
    top_posts = filtered_data.nlargest(10, 'Engagement_Count')
    bar_chart_fig = px.bar(
        top_posts,
        x="Post_ID",
        y="Engagement_Count",
        color="Platform",
        title="Top 10 Posts by Engagement",
        labels={"Engagement_Count": "Engagements", "Post_ID": "Post ID"}
    )

    # Pie chart: Engagement distribution by platform
    pie_chart_fig = px.pie(
        filtered_data,
        names="Platform",
        values="Engagement_Count",
        title="Engagement Distribution by Platform"
    )

    # Histogram: Distribution of engagement counts
    histogram_fig = px.histogram(
        filtered_data,
        x="Engagement_Count",
        nbins=20,
        title="Distribution of Engagement Counts",
        labels={"Engagement_Count": "Engagements"},
        color_discrete_sequence=["#003366"]  # Set histogram color
    )

    # Violin plot: Distribution of engagement by content type
    violin_fig = px.violin(
        filtered_data,
        y="Engagement_Count",
        x="Content_Type",
        box=True,
        points="all",
        title="Distribution of Engagement Counts by Content Type"
    )

    # Heatmap: Engagement count vs. platform and content type
    heatmap_fig = px.density_heatmap(
        filtered_data,
        x="Platform",
        y="Content_Type",
        z="Engagement_Count",
        title="Engagement Heatmap by Platform and Content Type",
        color_continuous_scale="Viridis"
    )

    return time_series_fig, bar_chart_fig, pie_chart_fig, histogram_fig, violin_fig, heatmap_fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
