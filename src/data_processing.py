import pandas as pd
import sqlite3
import numpy as np

def create_database():
    """Set up SQLite database with proper schema"""
    conn = sqlite3.connect('data/nfl_analytics.db')
    
    # Create tables
    conn.execute('''
    CREATE TABLE IF NOT EXISTS team_performance (
        team_id TEXT,
        team_name TEXT,
        week INTEGER,
        total_epa REAL,
        success_rate REAL,
        red_zone_efficiency REAL,
        third_down_rate REAL
    )
    ''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS player_efficiency (
        player_id TEXT,
        player_name TEXT,
        position TEXT,
        team TEXT,
        week INTEGER,
        epa_per_play REAL,
        success_rate REAL,
        targets INTEGER,
        completions INTEGER
    )
    ''')
    
    return conn

def process_team_data(pbp_df):
    """Transform play-by-play into team metrics"""
    # Calculate team EPA and success rates
    team_stats = pbp_df.groupby(['posteam', 'week']).agg({
        'epa': ['sum', 'mean'],
        'success': 'mean',
        'play_id': 'count'
    }).reset_index()
    
    # Flatten column names
    team_stats.columns = ['team', 'week', 'total_epa', 'epa_per_play', 'success_rate', 'total_plays']
    
    # Add red zone efficiency
    red_zone = pbp_df[pbp_df['yardline_100'] <= 20].groupby(['posteam', 'week'])['touchdown'].mean().reset_index()
    red_zone.columns = ['team', 'week', 'red_zone_td_rate']
    
    # Merge
    team_final = team_stats.merge(red_zone, on=['team', 'week'], how='left')
    
    return team_final

if __name__ == "__main__":
    # Load raw data
    pbp = pd.read_csv('data/raw_pbp_2024.csv')
    
    # Process
    team_data = process_team_data(pbp)
    
    # Save to database
    conn = create_database()
    team_data.to_sql('team_performance', conn, if_exists='replace', index=False)
    
    print("Data processing complete!")