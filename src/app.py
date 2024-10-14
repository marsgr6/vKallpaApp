import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sample DataFrame with dates in DD/MM/YYYY format (replace with your actual data)
df = pd.read_csv("https://raw.githubusercontent.com/marsgr6/r-scripts/refs/heads/master/data/comb.csv")

# Convert 'base' column to datetime, using dayfirst=True for DD/MM/YYYY format
df['base'] = pd.to_datetime(df['base'], dayfirst=True)
df.set_index('base', inplace=True)  # Set datetime column as index for resampling

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Comprehensive Time Series Dashboard"), className="text-center my-3")
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Resampling Frequency:"),
            dcc.Dropdown(
                id='resample-frequency',
                options=[
                    {'label': 'Hourly', 'value': 'H'},
                    {'label': 'Daily', 'value': 'D'},
                    {'label': 'Weekly', 'value': 'W'},
                    {'label': 'Monthly', 'value': 'M'}
                ],
                value='D',  # Default to daily
                style={'width': '100%'}
            )
        ], width=4),
    ], className="mb-4"),

    dbc.Row([
        # Panel 1: Temporal Series Plot (Summarized)
        dbc.Col(dcc.Graph(id='panel-1'), width=6),

        # Panel 2: Line Plot with Mean, Min, Max
        dbc.Col(dcc.Graph(id='panel-2'), width=6)
    ]),

    dbc.Row([
        # Panel 3: Box Plot Summarized by Hour of the Day
        dbc.Col(dcc.Graph(id='panel-3-hourly'), width=6),

        # Panel 4: Box Plot Summarized by Month of the Year
        dbc.Col(dcc.Graph(id='panel-4-monthly'), width=6)
    ])
], fluid=True)

# Callback to update the Panel 1: Temporal Series Plot
@app.callback(
    Output('panel-1', 'figure'),
    [Input('resample-frequency', 'value')]
)
def update_panel_1(resample_freq):
    # Resample the data based on the selected frequency
    resampled_df = df.resample(resample_freq).mean()

    # Create the temporal series plot (summarized)
    fig = px.line(resampled_df, y=['P Atteinte:HC', 'P Atteinte:HP'],
                  labels={'base': 'Date', 'value': 'Power (kW)'},
                  title=f"Temporal Series Resampled by {resample_freq}")
    
    return fig

# Callback to update Panel 2: Line Plot with Mean, Min, Max
@app.callback(
    Output('panel-2', 'figure'),
    [Input('resample-frequency', 'value')]
)
def update_panel_2(resample_freq):
    # Resample the data for mean, min, and max
    resampled_df = df.resample(resample_freq).agg(['mean', 'min', 'max'])
    
    # Create line plots for mean, min, and max
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HC']['mean'],
                             mode='lines', name='HC Mean', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HC']['min'],
                             mode='lines', name='HC Min', line=dict(color='lightblue', dash='dash')))
    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HC']['max'],
                             mode='lines', name='HC Max', line=dict(color='darkblue', dash='dash')))

    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HP']['mean'],
                             mode='lines', name='HP Mean', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HP']['min'],
                             mode='lines', name='HP Min', line=dict(color='lightcoral', dash='dash')))
    fig.add_trace(go.Scatter(x=resampled_df.index, y=resampled_df['P Atteinte:HP']['max'],
                             mode='lines', name='HP Max', line=dict(color='darkred', dash='dash')))

    fig.update_layout(title=f"Resampled Mean, Min, Max by {resample_freq}",
                      xaxis_title="Date", yaxis_title="Power (kW)")
    
    return fig

# Callback to update Panel 3: Box Plot by Hour of the Day
@app.callback(
    Output('panel-3-hourly', 'figure'),
    [Input('resample-frequency', 'value')]
)
def update_panel_3_hourly(resample_freq):
    # Summarize data by hour of the day
    df_reset = df.reset_index()
    df_reset['hour'] = df_reset['base'].dt.hour

    # Create box plot for hour of the day (0-23)
    fig = go.Figure()

    fig.add_trace(go.Box(y=df_reset['P Atteinte:HC'], x=df_reset['hour'],
                         name='HC by Hour of Day', boxmean='sd'))
    fig.add_trace(go.Box(y=df_reset['P Atteinte:HP'], x=df_reset['hour'],
                         name='HP by Hour of Day', boxmean='sd'))

    fig.update_layout(title="Box Plot Summarized by Hour of the Day",
                      xaxis_title="Hour of the Day", yaxis_title="Power (kW)")

    return fig

# Callback to update Panel 4: Box Plot by Month of the Year
@app.callback(
    Output('panel-4-monthly', 'figure'),
    [Input('resample-frequency', 'value')]
)
def update_panel_4_monthly(resample_freq):
    # Summarize data by month of the year
    df_reset = df.reset_index()
    df_reset['month'] = df_reset['base'].dt.month

    # Create box plot for month of the year (January to December)
    fig = go.Figure()

    fig.add_trace(go.Box(y=df_reset['P Atteinte:HC'], x=df_reset['month'],
                         name='HC by Month of Year', boxmean='sd'))
    fig.add_trace(go.Box(y=df_reset['P Atteinte:HP'], x=df_reset['month'],
                         name='HP by Month of Year', boxmean='sd'))

    fig.update_layout(title="Box Plot Summarized by Month of the Year",
                      xaxis_title="Month of the Year", yaxis_title="Power (kW)")

    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
