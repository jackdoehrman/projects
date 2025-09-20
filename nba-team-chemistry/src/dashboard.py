import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3

# Load data
conn = sqlite3.connect('data/nba_chemistry.db')
team_data = pd.read_sql('SELECT * FROM team_performance', conn)
player_data = pd.read_sql('SELECT * FROM player_chemistry', conn)

# Check what columns we actually have
print("Available columns in team_data:")
print(team_data.columns.tolist())
print("\nFirst few rows:")
print(team_data.head())

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Team Chemistry & Performance Analytics", 
            style={'text-align': 'center', 'color': '#1f2937', 'margin-bottom': '30px'}),
    
    # Team selection
    html.Div([
        html.Label("Select Teams to Compare:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': f"{row['TEAM_NAME']} ({row['TEAM_ABBREVIATION']})", 'value': row['TEAM_ABBREVIATION']} 
                    for _, row in team_data.iterrows()],
            value=team_data['TEAM_ABBREVIATION'].tolist(),
            multi=True,
            style={'margin-bottom': '20px'}
        )
    ]),
    
    # Key metrics cards
    html.Div(id='metrics-cards', style={'margin-bottom': '30px'}),
    
    # Charts
    html.Div([
        html.Div([
            dcc.Graph(id='chemistry-comparison')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='efficiency-analysis')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    html.Div([
        dcc.Graph(id='performance-breakdown')
    ]),
    
    # Team analysis table
    html.H3("Team Performance Breakdown", style={'margin-top': '40px'}),
    html.Div(id='team-analysis-table')
])

@app.callback(
    [Output('metrics-cards', 'children'),
     Output('chemistry-comparison', 'figure'),
     Output('efficiency-analysis', 'figure'), 
     Output('performance-breakdown', 'figure'),
     Output('team-analysis-table', 'children')],
    [Input('team-dropdown', 'value')]
)
def update_dashboard(selected_teams):
    # Filter data
    filtered_teams = team_data[team_data['TEAM_ABBREVIATION'].isin(selected_teams)]
    
    # Metrics Cards (using actual column names)
    cards = []
    for _, team in filtered_teams.iterrows():
        # Use actual column names from the data
        wins = team.get('W', team.get('wins', 0))
        losses = team.get('L', team.get('losses', 0))
        chemistry = team.get('CHEMISTRY_RATING', team.get('chemistry_rating', 'Unknown'))
        net_rating = team.get('NET_RATING', team.get('net_rating', 0))
        
        card = html.Div([
            html.H4(f"{team['TEAM_NAME']}", style={'margin': '0', 'color': '#1f2937'}),
            html.P(f"Record: {wins}-{losses}", style={'margin': '5px 0'}),
            html.P(f"Chemistry: {chemistry}", style={'margin': '5px 0', 'font-weight': 'bold'}),
            html.P(f"Net Rating: {net_rating:+.1f}", style={'margin': '5px 0'})
        ], style={
            'border': '1px solid #ddd', 
            'border-radius': '8px', 
            'padding': '15px', 
            'margin': '10px',
            'background-color': '#f8f9fa',
            'display': 'inline-block',
            'width': '200px',
            'vertical-align': 'top'
        })
        cards.append(card)
    
    # Chemistry Comparison Chart
    chemistry_col = 'CHEMISTRY_SCORE' if 'CHEMISTRY_SCORE' in filtered_teams.columns else 'PLUS_MINUS'
    chemistry_fig = px.bar(
        filtered_teams,
        x='TEAM_ABBREVIATION',
        y=chemistry_col,
        color='CHEMISTRY_RATING' if 'CHEMISTRY_RATING' in filtered_teams.columns else 'TEAM_NAME',
        title='Team Performance Comparison',
        labels={chemistry_col: 'Performance Score', 'TEAM_ABBREVIATION': 'Team'}
    )
    
    # Efficiency Analysis
    off_col = 'OFFENSIVE_RATING' if 'OFFENSIVE_RATING' in filtered_teams.columns else 'PTS'
    def_col = 'DEFENSIVE_RATING' if 'DEFENSIVE_RATING' in filtered_teams.columns else 'TOV'
    
    efficiency_fig = px.scatter(
        filtered_teams,
        x=def_col,
        y=off_col,
        size='W' if 'W' in filtered_teams.columns else 'GP',
        color='CHEMISTRY_RATING' if 'CHEMISTRY_RATING' in filtered_teams.columns else 'TEAM_NAME',
        hover_data=['TEAM_NAME', 'W_PCT'],
        title='Team Efficiency Analysis',
        labels={off_col: 'Offensive Metric', def_col: 'Defensive Metric'}
    )
    
    # Performance Breakdown (using available columns)
    performance_fig = go.Figure()
    
    for _, team in filtered_teams.iterrows():
        # Use available percentage columns
        metrics = []
        labels = []
        
        if 'FG_PCT' in team:
            metrics.append(team['FG_PCT'] * 100)
            labels.append('Field Goal %')
        if 'FG3_PCT' in team:
            metrics.append(team['FG3_PCT'] * 100)
            labels.append('3-Point %')
        if 'W_PCT' in team:
            metrics.append(team['W_PCT'] * 100)
            labels.append('Win %')
        
        if metrics:  # Only add if we have data
            performance_fig.add_trace(go.Scatterpolar(
                r=metrics,
                theta=labels,
                fill='toself',
                name=team['TEAM_ABBREVIATION']
            ))
    
    performance_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="Team Performance Radar Chart"
    )
    
    # Team Analysis Table (using available columns)
    display_columns = []
    column_configs = []
    
    # Always available columns
    display_columns.extend(['TEAM_NAME', 'TEAM_ABBREVIATION'])
    column_configs.extend([
        {'name': 'Team', 'id': 'TEAM_NAME'},
        {'name': 'Abbr', 'id': 'TEAM_ABBREVIATION'}
    ])
    
    # Conditional columns
    if 'W' in filtered_teams.columns:
        display_columns.append('W')
        column_configs.append({'name': 'Wins', 'id': 'W'})
    if 'L' in filtered_teams.columns:
        display_columns.append('L')
        column_configs.append({'name': 'Losses', 'id': 'L'})
    if 'W_PCT' in filtered_teams.columns:
        display_columns.append('W_PCT')
        column_configs.append({'name': 'Win %', 'id': 'W_PCT', 'format': {'specifier': '.3f'}})
    if 'PLUS_MINUS' in filtered_teams.columns:
        display_columns.append('PLUS_MINUS')
        column_configs.append({'name': 'Plus/Minus', 'id': 'PLUS_MINUS', 'format': {'specifier': '+.0f'}})
    if 'CHEMISTRY_RATING' in filtered_teams.columns:
        display_columns.append('CHEMISTRY_RATING')
        column_configs.append({'name': 'Chemistry', 'id': 'CHEMISTRY_RATING'})
    
    analysis_table = dash_table.DataTable(
        data=filtered_teams[display_columns].to_dict('records'),
        columns=column_configs,
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
    )
    
    return cards, chemistry_fig, efficiency_fig, performance_fig, analysis_table

if __name__ == '__main__':
    app.run(debug=True)