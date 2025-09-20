import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

# Load data
conn = sqlite3.connect('data/nfl_analytics.db')
df = pd.read_sql('SELECT * FROM team_performance', conn)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NFL Team Performance Analytics", style={'text-align': 'center'}),
    
    html.Div([
        html.Label("Select Teams:"),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in df['team'].unique()],
            value=df['team'].unique()[:5],
            multi=True
        )
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(id='epa-trend'),
        dcc.Graph(id='success-rate-comparison')
    ])
])

@app.callback(
    [Output('epa-trend', 'figure'),
     Output('success-rate-comparison', 'figure')],
    [Input('team-dropdown', 'value')]
)
def update_graphs(selected_teams):
    filtered_df = df[df['team'].isin(selected_teams)]
    
    # EPA Trend
    epa_fig = px.line(filtered_df, x='week', y='total_epa', color='team',
                      title='EPA Trend by Week')
    
    # Success Rate Comparison
    success_fig = px.box(filtered_df, x='team', y='success_rate',
                        title='Success Rate Distribution by Team')
    
    return epa_fig, success_fig

if __name__ == '__main__':
    app.run(debug=True)
