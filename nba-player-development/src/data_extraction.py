from nba_api.stats.endpoints import leaguedashplayerstats, playercareerstats, teamdashboardbygeneralsplits
from nba_api.stats.static import players, teams
import pandas as pd
import time
import sqlite3

def get_current_season_players():
    """Extract current season player stats"""
    print("Downloading current season player data...")
    
    # Get current season stats (2023-24)
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2023-24',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]
    
    print(f"Downloaded stats for {len(player_stats)} players")
    return player_stats

def get_rookie_sophomore_data():
    """Get data specifically for young players"""
    print("Getting rookie and sophomore data...")
    
    # Get players with 1-2 years experience
    young_players = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2023-24',
        season_type_all_star='Regular Season'
    ).get_data_frames()[0]
    
    # Filter for players likely to be young (we'll refine this)
    young_players = young_players[young_players['MIN'] >= 10]  # At least 10 min/game
    
    return young_players

def get_historical_comparison():
    """Get last 3 seasons for trend analysis"""
    seasons = ['2021-22', '2022-23', '2023-24']
    all_seasons = []
    
    for season in seasons:
        print(f"Downloading {season} data...")
        season_data = leaguedashplayerstats.LeagueDashPlayerStats(
            season=season,
            season_type_all_star='Regular Season'
        ).get_data_frames()[0]
        
        season_data['SEASON'] = season
        all_seasons.append(season_data)
        time.sleep(1)  # Be nice to the API
    
    return pd.concat(all_seasons, ignore_index=True)

def calculate_efficiency_metrics(df):
    """Add advanced efficiency calculations"""
    # True Shooting Percentage
    df['TS_PCT'] = df['PTS'] / (2 * (df['FGA'] + 0.44 * df['FTA']))
    
    # Player Efficiency Rating (simplified)
    df['PER_SIMPLE'] = (df['PTS'] + df['REB'] + df['AST'] + df['STL'] + df['BLK'] - 
                       df['TOV'] - (df['FGA'] - df['FGM']) - (df['FTA'] - df['FTM'])) / df['GP']
    
    # Usage Rate approximation
    df['USG_RATE'] = (df['FGA'] + 0.44 * df['FTA'] + df['TOV']) / df['MIN'] * 100
    
    # Development Score (custom metric)
    df['DEV_SCORE'] = (df['TS_PCT'] * 100 + df['AST'] + df['REB'] - df['TOV']) / df['USG_RATE'] * 10
    
    return df

if __name__ == "__main__":
    # Extract all data
    current_players = get_current_season_players()
    young_players = get_rookie_sophomore_data()
    historical_data = get_historical_comparison()
    
    # Add efficiency metrics
    current_players = calculate_efficiency_metrics(current_players)
    historical_data = calculate_efficiency_metrics(historical_data)
    
    # Save raw data
    current_players.to_csv('data/current_season_players.csv', index=False)
    historical_data.to_csv('data/historical_player_data.csv', index=False)
    
    print("Data extraction complete!")
    print(f"Current season: {len(current_players)} players")
    print(f"Historical data: {len(historical_data)} records")