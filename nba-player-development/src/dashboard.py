import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

# Load data
conn = sqlite3.connect('data/nba_development.db')
player_data = pd.read_sql('SELECT * FROM player_development', conn)
breakout_data = pd.read_sql('SELECT * FROM breakout_candidates', conn)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Player Development Analytics", 
            style={'text-align': 'center', 'color': '#1f2937', 'margin-bottom': '30px'}),
    
    # Control panel
    html.Div([
        html.Div([
            html.Label("Select Players:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='player-dropdown',
                options=[{'label': name, 'value': name} 
                        for name in sorted(player_data['PLAYER_NAME'].unique())],
                value=sorted(player_data['PLAYER_NAME'].unique())[:5],
                multi=True,
                style={'margin-bottom': '10px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '4%'}),
        
        html.Div([
            html.Label("Select Metric:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Points Per Game', 'value': 'PTS'},
                    {'label': 'True Shooting %', 'value': 'TS_PCT'},
                    {'label': 'Usage Rate', 'value': 'USG_RATE'},
                    {'label': 'Assists', 'value': 'AST'}
                ],
                value='PTS'
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'margin-bottom': '30px'}),
    
    # Charts
    html.Div([
        dcc.Graph(id='development-trend'),
        dcc.Graph(id='improvement-analysis')
    ]),
    
    # Breakout candidates table
    html.H3("Top Breakout Candidates", style={'margin-top': '40px', 'color': '#1f2937'}),
    html.Div(id='breakout-table')
])

@app.callback(
    [Output('development-trend', 'figure'),
     Output('improvement-analysis', 'figure'),
     Output('breakout-table', 'children')],
    [Input('player-dropdown', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_dashboard(selected_players, selected_metric):
    # Filter data
    filtered_data = player_data[player_data['PLAYER_NAME'].isin(selected_players)]
    
    # Development trend chart
    metric_name = selected_metric.replace('_', ' ').title()
    trend_fig = px.line(
        filtered_data, 
        x='SEASON', 
        y=selected_metric, 
        color='PLAYER_NAME',
        title=f'{metric_name} Development Over Time',
        markers=True
    )
    trend_fig.update_layout(
        xaxis_title="Season",
        yaxis_title=metric_name,
        hovermode='x unified'
    )
    
    # Improvement analysis (scatter plot)
    improvement_fig = px.scatter(
        filtered_data,
        x='USG_RATE',
        y=selected_metric,
        size='MIN',
        color='PLAYER_NAME',
        title=f'Usage Rate vs {metric_name}',
        hover_data=['SEASON', 'TEAM_ABBREVIATION']
    )
    
    # Breakout candidates table
    breakout_table = dash_table.DataTable(
        data=breakout_data.head(10).to_dict('records'),
        columns=[
            {'name': 'Player', 'id': 'PLAYER_NAME'},
            {'name': 'Team', 'id': 'TEAM_ABBREVIATION'},
            {'name': 'Age', 'id': 'AGE'},
            {'name': 'PPG', 'id': 'PTS', 'type': 'numeric', 'format': {'specifier': '.1f'}},
            {'name': 'TS%', 'id': 'TS_PCT', 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {'name': 'Breakout Prob', 'id': 'BREAKOUT_PROB', 'type': 'numeric', 'format': {'specifier': '.3f'}}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{BREAKOUT_PROB} > 0.7'},
                'backgroundColor': '#d4edda',
                'color': 'black',
            }
        ]
    )
    
    return trend_fig, improvement_fig, breakout_table

if __name__ == '__main__':
    app.run(debug=True)