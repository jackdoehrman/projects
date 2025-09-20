import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import numpy as np

# Load data
conn = sqlite3.connect('data/nba_shot_analytics.db')
shot_data = pd.read_sql('SELECT * FROM shot_attempts', conn)
player_data = pd.read_sql('SELECT * FROM player_shooting', conn)
team_data = pd.read_sql('SELECT * FROM team_efficiency', conn)

# Debug: Check what columns we actually have
print("Shot data columns:", shot_data.columns.tolist())
print("Player data columns:", player_data.columns.tolist())
print("Team data columns:", team_data.columns.tolist())

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Shot Selection & Efficiency Analytics", 
            style={'text-align': 'center', 'color': '#1f2937', 'margin-bottom': '30px'}),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Select Player:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='player-dropdown',
                options=[{'label': name, 'value': name} 
                        for name in sorted(player_data['player_name'].unique()) if not player_data.empty],
                value=player_data['player_name'].iloc[0] if len(player_data) > 0 else "Sample Player",
                style={'margin-bottom': '10px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '4%'}),
        
        html.Div([
            html.Label("Analysis Type:", style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='analysis-dropdown',
                options=[
                    {'label': 'Shot Distribution', 'value': 'shot_distribution'},
                    {'label': 'Efficiency Analysis', 'value': 'efficiency_analysis'},
                    {'label': 'Team Comparison', 'value': 'team_comparison'},
                    {'label': 'Shot Distance', 'value': 'distance_analysis'}
                ],
                value='shot_distribution'
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'margin-bottom': '30px'}),
    
    # Player stats cards
    html.Div(id='player-stats-cards', style={'margin-bottom': '30px'}),
    
    # Main visualization
    html.Div([
        dcc.Graph(id='main-chart', style={'height': '600px'})
    ]),
    
    # Secondary charts
    html.Div([
        html.Div([
            dcc.Graph(id='efficiency-chart')
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='selection-chart')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    # Analysis table
    html.H3("Player Shooting Analysis", style={'margin-top': '40px'}),
    html.Div(id='analysis-table')
])

@app.callback(
    [Output('player-stats-cards', 'children'),
     Output('main-chart', 'figure'),
     Output('efficiency-chart', 'figure'),
     Output('selection-chart', 'figure'),
     Output('analysis-table', 'children')],
    [Input('player-dropdown', 'value'),
     Input('analysis-dropdown', 'value')]
)
def update_dashboard(selected_player, analysis_type):
    
    # Player stats cards
    if selected_player and not player_data.empty:
        player_stats = player_data[player_data['player_name'] == selected_player]
        
        if not player_stats.empty:
            player_stats = player_stats.iloc[0]
            
            cards = html.Div([
                html.Div([
                    html.H4("Overall", style={'margin': '0', 'color': '#1f2937'}),
                    html.P(f"FG%: {player_stats['overall_fg_pct']:.3f}", style={'margin': '5px 0'}),
                    html.P(f"Attempts: {player_stats['total_attempts']}", style={'margin': '5px 0'})
                ], style={'border': '1px solid #ddd', 'padding': '15px', 'margin': '10px', 
                         'display': 'inline-block', 'width': '150px', 'background-color': '#f8f9fa'}),
                
                html.Div([
                    html.H4("At Rim", style={'margin': '0', 'color': '#1f2937'}),
                    html.P(f"FG%: {player_stats['at_rim_fg_pct']:.3f}", style={'margin': '5px 0'}),
                    html.P(f"Attempts: {player_stats['at_rim_attempts']}", style={'margin': '5px 0'})
                ], style={'border': '1px solid #ddd', 'padding': '15px', 'margin': '10px',
                         'display': 'inline-block', 'width': '150px', 'background-color': '#e8f5e8'}),
                
                html.Div([
                    html.H4("3-Point", style={'margin': '0', 'color': '#1f2937'}),
                    html.P(f"3P%: {player_stats['three_point_pct']:.3f}", style={'margin': '5px 0'}),
                    html.P(f"Attempts: {player_stats['three_point_attempts']}", style={'margin': '5px 0'})
                ], style={'border': '1px solid #ddd', 'padding': '15px', 'margin': '10px',
                         'display': 'inline-block', 'width': '150px', 'background-color': '#e8f0ff'}),
                
                html.Div([
                    html.H4("Selection Score", style={'margin': '0', 'color': '#1f2937'}),
                    html.P(f"Score: {player_stats['shot_selection_score']:.1f}", 
                          style={'margin': '5px 0', 'font-size': '18px', 'font-weight': 'bold'}),
                ], style={'border': '1px solid #ddd', 'padding': '15px', 'margin': '10px',
                         'display': 'inline-block', 'width': '150px', 'background-color': '#fff3cd'})
            ])
        else:
            cards = html.Div("Player not found")
    else:
        cards = html.Div("No player data available")
    
    # Main chart based on analysis type
    if analysis_type == 'shot_distribution' and not player_data.empty:
        # Shot distribution pie chart
        if selected_player:
            player_stats = player_data[player_data['player_name'] == selected_player]
            if not player_stats.empty:
                player_stats = player_stats.iloc[0]
                
                shot_types = ['At Rim', '3-Point', 'Mid-Range']
                shot_counts = [
                    player_stats['at_rim_attempts'],
                    player_stats['three_point_attempts'],
                    player_stats['midrange_attempts']
                ]
                
                main_fig = px.pie(
                    values=shot_counts,
                    names=shot_types,
                    title=f'{selected_player} - Shot Distribution',
                    color_discrete_sequence=['#2E8B57', '#4169E1', '#FF6347']
                )
            else:
                main_fig = px.pie(title="Player not found")
        else:
            main_fig = px.pie(title="Select a player")
            
    elif analysis_type == 'efficiency_analysis' and not player_data.empty:
        # Efficiency bar chart
        if selected_player:
            player_stats = player_data[player_data['player_name'] == selected_player]
            if not player_stats.empty:
                player_stats = player_stats.iloc[0]
                
                zones = ['At Rim', '3-Point', 'Mid-Range']
                percentages = [
                    player_stats['at_rim_fg_pct'],
                    player_stats['three_point_pct'], 
                    player_stats['midrange_fg_pct']
                ]
                attempts = [
                    player_stats['at_rim_attempts'],
                    player_stats['three_point_attempts'],
                    player_stats['midrange_attempts']
                ]
                
                main_fig = go.Figure()
                main_fig.add_trace(go.Bar(
                    x=zones,
                    y=percentages,
                    text=[f"{p:.1%}<br>{a} attempts" for p, a in zip(percentages, attempts)],
                    textposition='auto',
                    marker_color=['#2E8B57', '#4169E1', '#FF6347']
                ))
                
                main_fig.update_layout(
                    title=f'{selected_player} - Shooting Efficiency by Zone',
                    yaxis_title='Field Goal Percentage',
                    yaxis=dict(tickformat='.1%')
                )
            else:
                main_fig = px.bar(title="Player not found")
        else:
            main_fig = px.bar(title="Select a player")
            
    elif analysis_type == 'team_comparison' and not team_data.empty:
        # Team comparison scatter
        main_fig = px.scatter(
            team_data,
            x='three_point_pct',
            y='close_range_pct',
            size='overall_efficiency_score',
            color='overall_efficiency_score',
            hover_data=['team_name'],
            title='Team Shooting Efficiency Comparison',
            labels={
                'three_point_pct': '3-Point Percentage',
                'close_range_pct': 'Close Range Percentage',
                'overall_efficiency_score': 'Efficiency Score'
            }
        )
        main_fig.update_layout(
            xaxis=dict(tickformat='.1%'),
            yaxis=dict(tickformat='.1%')
        )
        
    else:  # distance_analysis or fallback
        # Simple distance analysis using shot data
        if not shot_data.empty and 'SHOT_DISTANCE' in shot_data.columns:
            # Use actual shot data column names
            player_col = 'PLAYER_NAME' if 'PLAYER_NAME' in shot_data.columns else shot_data.columns[0]
            
            if selected_player and player_col in shot_data.columns:
                player_shots = shot_data[shot_data[player_col] == selected_player]
            else:
                player_shots = shot_data
            
            if not player_shots.empty:
                # Create distance histogram
                main_fig = px.histogram(
                    player_shots,
                    x='SHOT_DISTANCE',
                    nbins=20,
                    title=f'Shot Distance Distribution - {selected_player}' if selected_player else 'Shot Distance Distribution'
                )
                main_fig.update_layout(
                    xaxis_title='Shot Distance (feet)',
                    yaxis_title='Number of Shots'
                )
            else:
                main_fig = px.histogram(title="No shot data available")
        else:
            main_fig = px.bar(title="No distance data available")
    
    # Efficiency comparison chart
    if not player_data.empty:
        top_players = player_data.nlargest(min(5, len(player_data)), 'shot_selection_score')
        
        efficiency_fig = px.bar(
            top_players,
            x='player_name',
            y='shot_selection_score',
            title='Top Players - Shot Selection Scores',
            labels={'shot_selection_score': 'Selection Score', 'player_name': 'Player'},
            color='shot_selection_score',
            color_continuous_scale='viridis'
        )
        efficiency_fig.update_xaxes(tickangle=45)
    else:
        efficiency_fig = px.bar(title="No player data available")
    
    # Player efficiency scatter
    if not player_data.empty:
        selection_fig = px.scatter(
            player_data,
            x='overall_fg_pct',
            y='shot_selection_score',
            size='total_attempts',
            hover_data=['player_name', 'team_name'],
            title='Shooting Efficiency vs Shot Selection',
            labels={
                'overall_fg_pct': 'Overall FG%',
                'shot_selection_score': 'Shot Selection Score'
            }
        )
        selection_fig.update_layout(xaxis=dict(tickformat='.1%'))
    else:
        selection_fig = px.scatter(title="No data available")
    
    # Analysis table
    if not player_data.empty:
        table_data = player_data.sort_values('shot_selection_score', ascending=False)
        
        analysis_table = dash_table.DataTable(
            data=table_data.to_dict('records'),
            columns=[
                {'name': 'Player', 'id': 'player_name'},
                {'name': 'Team', 'id': 'team_name'},
                {'name': 'Total FG%', 'id': 'overall_fg_pct', 'format': {'specifier': '.3f'}},
                {'name': 'At Rim FG%', 'id': 'at_rim_fg_pct', 'format': {'specifier': '.3f'}},
                {'name': '3P%', 'id': 'three_point_pct', 'format': {'specifier': '.3f'}},
                {'name': 'Selection Score', 'id': 'shot_selection_score', 'format': {'specifier': '.1f'}}
            ],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
            page_size=10
        )
    else:
        analysis_table = html.Div("No analysis data available")
    
    return cards, main_fig, efficiency_fig, selection_fig, analysis_table

if __name__ == '__main__':
    app.run(debug=True)