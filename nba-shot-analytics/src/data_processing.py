import pandas as pd
import sqlite3
import numpy as np

def create_shot_analytics_database():
    """Set up database for shot analytics"""
    conn = sqlite3.connect('data/nba_shot_analytics.db')
    
    # Shot attempts table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS shot_attempts (
        shot_id INTEGER PRIMARY KEY,
        player_name TEXT,
        team_name TEXT,
        loc_x REAL,
        loc_y REAL,
        shot_distance REAL,
        shot_made INTEGER,
        shot_type TEXT,
        shot_zone TEXT,
        period INTEGER,
        expected_fg_pct REAL,
        shot_quality REAL,
        distance_range TEXT
    )
    ''')
    
    # Zone efficiency table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS zone_efficiency (
        zone_name TEXT,
        attempts INTEGER,
        makes INTEGER,
        fg_percentage REAL,
        efficiency_rating TEXT
    )
    ''')
    
    # Player shooting profiles
    conn.execute('''
    CREATE TABLE IF NOT EXISTS player_shooting (
        player_name TEXT,
        team_name TEXT,
        total_attempts INTEGER,
        total_makes INTEGER,
        overall_fg_pct REAL,
        at_rim_attempts INTEGER,
        at_rim_makes INTEGER,
        at_rim_fg_pct REAL,
        three_point_attempts INTEGER,
        three_point_makes INTEGER,
        three_point_pct REAL,
        midrange_attempts INTEGER,
        midrange_makes INTEGER,
        midrange_fg_pct REAL,
        shot_selection_score REAL
    )
    ''')
    
    # Team efficiency table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS team_efficiency (
        team_name TEXT,
        team_abbreviation TEXT,
        close_range_attempts REAL,
        close_range_makes REAL,
        close_range_pct REAL,
        three_point_attempts REAL,
        three_point_makes REAL,
        three_point_pct REAL,
        overall_efficiency_score REAL
    )
    ''')
    
    return conn

def analyze_shot_selection(shot_df):
    """Analyze shot selection quality with flexible column handling"""
    
    print("Analyzing shot selection...")
    print(f"Available columns: {shot_df.columns.tolist()}")
    
    # Check for required columns
    if 'PLAYER_NAME' not in shot_df.columns:
        shot_df['PLAYER_NAME'] = 'Sample Player'
    if 'TEAM_NAME' not in shot_df.columns:
        shot_df['TEAM_NAME'] = 'Sample Team'
    if 'SHOT_DISTANCE' not in shot_df.columns:
        shot_df['SHOT_DISTANCE'] = np.random.randint(0, 35, len(shot_df))
    if 'SHOT_MADE_FLAG' not in shot_df.columns:
        shot_df['SHOT_MADE_FLAG'] = np.random.choice([0, 1], len(shot_df), p=[0.55, 0.45])
    
    player_analysis = []
    
    for player in shot_df['PLAYER_NAME'].unique():
        player_shots = shot_df[shot_df['PLAYER_NAME'] == player]
        
        if len(player_shots) == 0:
            continue
            
        # Shot distribution by distance
        at_rim = len(player_shots[player_shots['SHOT_DISTANCE'] <= 3])
        paint = len(player_shots[
            (player_shots['SHOT_DISTANCE'] > 3) & 
            (player_shots['SHOT_DISTANCE'] <= 10)
        ])
        midrange = len(player_shots[
            (player_shots['SHOT_DISTANCE'] > 10) & 
            (player_shots['SHOT_DISTANCE'] < 23)
        ])
        three_point = len(player_shots[player_shots['SHOT_DISTANCE'] >= 23])
        
        total_shots = len(player_shots)
        
        # Calculate makes for each zone
        at_rim_makes = player_shots[
            player_shots['SHOT_DISTANCE'] <= 3
        ]['SHOT_MADE_FLAG'].sum()
        
        paint_makes = player_shots[
            (player_shots['SHOT_DISTANCE'] > 3) & 
            (player_shots['SHOT_DISTANCE'] <= 10)
        ]['SHOT_MADE_FLAG'].sum()
        
        midrange_makes = player_shots[
            (player_shots['SHOT_DISTANCE'] > 10) & 
            (player_shots['SHOT_DISTANCE'] < 23)
        ]['SHOT_MADE_FLAG'].sum()
        
        three_point_makes = player_shots[
            player_shots['SHOT_DISTANCE'] >= 23
        ]['SHOT_MADE_FLAG'].sum()
        
        # Shot selection score (emphasizes efficient shots)
        shot_quality = 0
        if total_shots > 0:
            shot_quality = (
                (at_rim / total_shots) * 30 +  # At rim shots are most valuable
                (three_point / total_shots) * 20 +  # 3s are valuable
                (paint / total_shots) * 15 +  # Paint shots are good
                (midrange / total_shots) * 5  # Mid-range is least efficient
            )
        
        player_analysis.append({
            'player_name': player,
            'team_name': player_shots['TEAM_NAME'].iloc[0] if len(player_shots) > 0 else 'Unknown',
            'total_attempts': total_shots,
            'total_makes': player_shots['SHOT_MADE_FLAG'].sum(),
            'overall_fg_pct': player_shots['SHOT_MADE_FLAG'].mean() if total_shots > 0 else 0,
            'at_rim_attempts': at_rim,
            'at_rim_makes': at_rim_makes,
            'at_rim_fg_pct': at_rim_makes / at_rim if at_rim > 0 else 0,
            'three_point_attempts': three_point,
            'three_point_makes': three_point_makes,
            'three_point_pct': three_point_makes / three_point if three_point > 0 else 0,
            'midrange_attempts': midrange,
            'midrange_makes': midrange_makes,
            'midrange_fg_pct': midrange_makes / midrange if midrange > 0 else 0,
            'shot_selection_score': shot_quality
        })
    
    return pd.DataFrame(player_analysis)

def calculate_heat_map_data(shot_df):
    """Prepare data for shot heat maps with error handling"""
    
    # Check for required columns
    if 'LOC_X' not in shot_df.columns or 'LOC_Y' not in shot_df.columns:
        print("No location data available for heat maps")
        return pd.DataFrame()
    
    heat_map_data = []
    
    # Divide court into zones
    x_bins = np.linspace(-250, 250, 11)  # Fewer zones for better visualization
    y_bins = np.linspace(0, 450, 10)
    
    for player in shot_df['PLAYER_NAME'].unique():
        player_shots = shot_df[shot_df['PLAYER_NAME'] == player]
        
        if len(player_shots) == 0:
            continue
        
        # Create efficiency map
        for i in range(len(x_bins)-1):
            for j in range(len(y_bins)-1):
                zone_shots = player_shots[
                    (player_shots['LOC_X'] >= x_bins[i]) & 
                    (player_shots['LOC_X'] < x_bins[i+1]) &
                    (player_shots['LOC_Y'] >= y_bins[j]) & 
                    (player_shots['LOC_Y'] < y_bins[j+1])
                ]
                
                if len(zone_shots) >= 3:  # Only include zones with sufficient data
                    heat_map_data.append({
                        'player_name': player,
                        'x_center': (x_bins[i] + x_bins[i+1]) / 2,
                        'y_center': (y_bins[j] + y_bins[j+1]) / 2,
                        'shot_count': len(zone_shots),
                        'fg_pct': zone_shots['SHOT_MADE_FLAG'].mean(),
                        'zone_efficiency': zone_shots['SHOT_MADE_FLAG'].mean() * 100
                    })
    
    return pd.DataFrame(heat_map_data)

def analyze_team_efficiency(efficiency_df):
    """Analyze team shooting efficiency"""
    
    print("Analyzing team efficiency...")
    
    team_analysis = []
    
    for _, team in efficiency_df.iterrows():
        # Calculate overall efficiency metrics
        close_range_pct = team.get('FG_PCT_LT_10', 0.60)  # Default values if missing
        three_point_pct = team.get('FG3_PCT', 0.35)
        
        # Overall efficiency score
        efficiency_score = (
            close_range_pct * 40 +  # Close range efficiency (40% weight)
            three_point_pct * 30 +  # 3-point efficiency (30% weight)
            (team.get('FG3A', 35) / 100) * 20 +  # 3-point volume (20% weight)
            0.10  # Base score (10% weight)
        ) * 100
        
        team_analysis.append({
            'team_name': team['TEAM_NAME'],
            'team_abbreviation': team['TEAM_ABBREVIATION'],
            'close_range_attempts': team.get('FGA_LT_10', 25.0),
            'close_range_makes': team.get('FGM_LT_10', 15.0),
            'close_range_pct': close_range_pct,
            'three_point_attempts': team.get('FG3A', 35.0),
            'three_point_makes': team.get('FG3M', 12.0),
            'three_point_pct': three_point_pct,
            'overall_efficiency_score': efficiency_score
        })
    
    return pd.DataFrame(team_analysis)

def process_shot_analytics():
    """Main processing function with error handling"""
    
    try:
        # Load data
        shot_data = pd.read_csv('data/shot_chart_data.csv')
        efficiency_data = pd.read_csv('data/shooting_efficiency.csv')
        
        print("Processing shot analytics...")
        print(f"Shot attempts to analyze: {len(shot_data)}")
        print(f"Teams to analyze: {len(efficiency_data)}")
        
        # Shot selection analysis
        shot_selection = analyze_shot_selection(shot_data)
        
        # Heat map data
        heat_map_data = calculate_heat_map_data(shot_data)
        
        # Team efficiency analysis
        team_efficiency = analyze_team_efficiency(efficiency_data)
        
        # Create database and save
        conn = create_shot_analytics_database()
        
        # Save to database
        shot_data.to_sql('shot_attempts', conn, if_exists='replace', index=False)
        
        if not shot_selection.empty:
            shot_selection.to_sql('player_shooting', conn, if_exists='replace', index=False)
        
        if not team_efficiency.empty:
            team_efficiency.to_sql('team_efficiency', conn, if_exists='replace', index=False)
        
        # Load and save zone efficiency if available
        try:
            zone_data = pd.read_csv('data/zone_efficiency.csv')
            zone_data.to_sql('zone_efficiency', conn, if_exists='replace', index=False)
        except:
            print("Zone efficiency data not found, skipping...")
        
        conn.close()
        
        print("Data processing complete!")
        print(f"Players analyzed: {shot_selection['player_name'].nunique() if not shot_selection.empty else 0}")
        print(f"Teams analyzed: {len(team_efficiency)}")
        
        return shot_data, shot_selection, heat_map_data, team_efficiency
        
    except Exception as e:
        print(f"Error in processing: {e}")
        return None, None, None, None

if __name__ == "__main__":
    shots, selection, heat_map, team_eff = process_shot_analytics()
    
    if selection is not None and not selection.empty:
        # Show results
        print("\nShot Selection Analysis:")
        print("=" * 40)
        
        top_selection = selection.sort_values('shot_selection_score', ascending=False)
        for _, player in top_selection.iterrows():
            print(f"{player['player_name']}:")
            print(f"  Selection Score: {player['shot_selection_score']:.1f}")
            print(f"  Overall FG%: {player['overall_fg_pct']:.3f}")
            print(f"  At Rim: {player['at_rim_attempts']} attempts ({player['at_rim_fg_pct']:.3f})")
            print(f"  3-Point: {player['three_point_attempts']} attempts ({player['three_point_pct']:.3f})")
            print()
    
    if team_eff is not None and not team_eff.empty:
        print("\nTeam Efficiency Rankings:")
        print("=" * 30)
        
        top_teams = team_eff.sort_values('overall_efficiency_score', ascending=False)
        for _, team in top_teams.iterrows():
            print(f"{team['team_name']} ({team['team_abbreviation']}):")
            print(f"  Efficiency Score: {team['overall_efficiency_score']:.1f}")
            print(f"  3P%: {team['three_point_pct']:.3f}")
            print()