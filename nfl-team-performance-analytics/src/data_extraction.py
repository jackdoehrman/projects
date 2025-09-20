import nfl_data_py as nfl
import pandas as pd
import sqlite3
from datetime import datetime

def extract_season_data(year=2024):
    """Extract current season NFL data"""
    print("Downloading NFL data...")
    
    # Get play-by-play data (this is the gold mine)
    pbp_data = nfl.import_pbp_data([year])
    
    # Get team stats
    team_stats = nfl.import_team_desc()
    
    # Get player stats
    player_stats = nfl.import_seasonal_data([year])
    
    print(f"Downloaded {len(pbp_data)} plays")
    return pbp_data, team_stats, player_stats

if __name__ == "__main__":
    pbp, teams, players = extract_season_data()
    
    # Save raw data
    pbp.to_csv('data/raw_pbp_2024.csv', index=False)
    players.to_csv('data/raw_player_stats_2024.csv', index=False)
    print("Raw data saved!")
