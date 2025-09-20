from nba_api.stats.endpoints import teamdashlineups, leaguedashteamstats, teamdashboardbygeneralsplits
from nba_api.stats.endpoints import leaguedashplayerstats, teamplayerdashboard
import pandas as pd
import time
import sqlite3

def create_sample_lineup_data():
    """Create realistic sample lineup data"""
    print("Creating sample lineup data...")
    
    sample_lineups = {
        'TEAM_ID': [1610612738, 1610612738, 1610612738, 1610612747, 1610612747],
        'TEAM_NAME': ['Boston Celtics', 'Boston Celtics', 'Boston Celtics', 'Los Angeles Lakers', 'Los Angeles Lakers'],
        'GROUP_NAME': [
            'J. Tatum - J. Brown - K. Porzingis - D. White - J. Holiday',
            'J. Tatum - J. Brown - A. Horford - D. White - J. Holiday', 
            'J. Tatum - J. Brown - K. Porzingis - M. Smart - R. Williams',
            'L. James - A. Davis - D. Russell - A. Reaves - R. Hachimura',
            'L. James - A. Davis - D. Russell - A. Reaves - C. Wood'
        ],
        'MIN': [245.2, 198.7, 167.3, 278.5, 156.8],
        'PLUS_MINUS': [+42, +28, +15, +38, +12],
        'OFF_RATING': [118.5, 115.2, 112.8, 116.7, 110.4],
        'DEF_RATING': [108.2, 110.5, 112.1, 109.8, 115.2],
        'NET_RATING': [+10.3, +4.7, +0.7, +6.9, -4.8],
        'PACE': [98.5, 96.8, 95.2, 100.2, 102.1],
        'TS_PCT': [0.612, 0.587, 0.568, 0.598, 0.542]
    }
    
    return pd.DataFrame(sample_lineups)

def get_team_lineup_data():
    """Extract team lineup combinations and their performance"""
    print("Downloading team lineup data...")
    
    try:
        # Get all teams first
        teams = leaguedashteamstats.LeagueDashTeamStats(season='2023-24').get_data_frames()[0]
        team_ids = teams['TEAM_ID'].tolist()[:3]  # Limit to 3 teams for demo
        
        all_lineups = []
        
        for team_id in team_ids:
            try:
                print(f"Getting lineup data for team {team_id}...")
                lineup_data = teamdashlineups.TeamDashLineups(
                    team_id=team_id,
                    season='2023-24',
                    season_type_all_star='Regular Season'
                ).get_data_frames()[0]
                
                lineup_data['TEAM_ID'] = team_id
                
                # Check what columns we actually have
                print(f"Columns available: {lineup_data.columns.tolist()}")
                
                all_lineups.append(lineup_data)
                time.sleep(1)  # Be nice to the API
                
            except Exception as e:
                print(f"Error getting data for team {team_id}: {e}")
                continue
        
        if all_lineups:
            combined_data = pd.concat(all_lineups, ignore_index=True)
            print(f"Final columns: {combined_data.columns.tolist()}")
            return combined_data
        else:
            return create_sample_lineup_data()
            
    except Exception as e:
        print(f"API Error: {e}")
        print("Using sample data instead...")
        return create_sample_lineup_data()

def create_sample_player_data():
    """Create sample player data"""
    sample_players = {
        'PLAYER_NAME': ['Jayson Tatum', 'Jaylen Brown', 'LeBron James', 'Anthony Davis', 'Stephen Curry'],
        'TEAM_ABBREVIATION': ['BOS', 'BOS', 'LAL', 'LAL', 'GSW'],
        'MIN': [35.7, 33.2, 35.3, 35.5, 32.7],
        'PTS': [26.9, 23.0, 25.7, 24.7, 26.4],
        'AST': [4.9, 3.6, 8.3, 3.5, 5.1],
        'REB': [8.1, 5.5, 7.3, 12.6, 4.5],
        'PLUS_MINUS': [+156, +98, +87, +112, +145],
        'OFF_RATING': [115.2, 112.8, 114.5, 116.2, 118.9],
        'DEF_RATING': [110.5, 112.1, 116.8, 108.9, 114.2],
        'NET_RATING': [+4.7, +0.7, -2.3, +7.3, +4.7]
    }
    
    return pd.DataFrame(sample_players)

def get_player_chemistry_data():
    """Get individual player stats for chemistry analysis"""
    print("Getting player chemistry data...")
    
    try:
        # Get player stats
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2023-24',
            season_type_all_star='Regular Season'
        ).get_data_frames()[0]
        
        # Focus on key players
        key_players = player_stats[player_stats['MIN'] >= 20].head(20)
        return key_players
        
    except Exception as e:
        print(f"Error getting player data: {e}")
        return create_sample_player_data()

def calculate_chemistry_metrics(lineup_df, player_df):
    """Calculate advanced chemistry metrics with flexible column names"""
    
    # Check what columns exist and map them
    columns_mapping = {}
    
    # Find the correct column names
    for col in lineup_df.columns:
        if 'NET' in col.upper() and 'RATING' in col.upper():
            columns_mapping['net_rating'] = col
        elif 'OFF' in col.upper() and 'RATING' in col.upper():
            columns_mapping['off_rating'] = col
        elif 'DEF' in col.upper() and 'RATING' in col.upper():
            columns_mapping['def_rating'] = col
        elif 'PLUS_MINUS' in col.upper():
            columns_mapping['plus_minus'] = col
        elif 'MIN' in col.upper():
            columns_mapping['minutes'] = col
    
    print(f"Found columns: {columns_mapping}")
    
    # Calculate metrics using available columns
    if 'net_rating' in columns_mapping:
        net_col = columns_mapping['net_rating']
    elif 'off_rating' in columns_mapping and 'def_rating' in columns_mapping:
        # Calculate net rating if not available
        off_col = columns_mapping['off_rating']
        def_col = columns_mapping['def_rating']
        lineup_df['NET_RATING'] = lineup_df[off_col] - lineup_df[def_col]
        net_col = 'NET_RATING'
    else:
        # Use a default if no rating columns
        lineup_df['NET_RATING'] = 0
        net_col = 'NET_RATING'
    
    # Efficiency score
    if net_col in lineup_df.columns:
        lineup_df['EFFICIENCY_SCORE'] = lineup_df[net_col]
    else:
        lineup_df['EFFICIENCY_SCORE'] = 0
    
    # Impact score
    if 'plus_minus' in columns_mapping and 'minutes' in columns_mapping:
        plus_col = columns_mapping['plus_minus']
        min_col = columns_mapping['minutes']
        lineup_df['IMPACT_SCORE'] = lineup_df[plus_col] / lineup_df[min_col] * 100
    else:
        lineup_df['IMPACT_SCORE'] = 0
    
    return lineup_df

if __name__ == "__main__":
    # Extract all data
    lineup_data = get_team_lineup_data()
    player_data = get_player_chemistry_data()
    
    # Show what we got
    print("\nLineup data shape:", lineup_data.shape)
    print("Lineup columns:", lineup_data.columns.tolist())
    
    # Calculate advanced metrics
    lineup_data = calculate_chemistry_metrics(lineup_data, player_data)
    
    # Save raw data
    lineup_data.to_csv('data/team_lineups.csv', index=False)
    player_data.to_csv('data/player_chemistry.csv', index=False)
    
    print("Data extraction complete!")
    print(f"Lineup combinations: {len(lineup_data)}")
    print(f"Players analyzed: {len(player_data)}")
    
    # Show sample data
    print("\nSample lineup data:")
    print(lineup_data.head())