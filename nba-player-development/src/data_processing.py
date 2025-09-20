import pandas as pd
import sqlite3
import numpy as np

def create_development_database():
    """Set up database for player development analytics"""
    conn = sqlite3.connect('data/nba_development.db')
    
    # Player development table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS player_development (
        player_id INTEGER,
        player_name TEXT,
        season TEXT,
        age INTEGER,
        team TEXT,
        games_played INTEGER,
        minutes_per_game REAL,
        points_per_game REAL,
        rebounds_per_game REAL,
        assists_per_game REAL,
        ts_percentage REAL,
        usage_rate REAL,
        development_score REAL,
        improvement_rating TEXT
    )
    ''')
    
    # Breakout candidates table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS breakout_candidates (
        player_id INTEGER,
        player_name TEXT,
        current_age INTEGER,
        breakout_probability REAL,
        key_strengths TEXT,
        development_areas TEXT,
        projected_improvement REAL
    )
    ''')
    
    return conn

def calculate_year_over_year_improvement(df):
    """Calculate player improvement metrics"""
    # Sort by player and season
    df_sorted = df.sort_values(['PLAYER_NAME', 'SEASON'])
    
    # Calculate year-over-year changes
    df_sorted['PREV_PTS'] = df_sorted.groupby('PLAYER_NAME')['PTS'].shift(1)
    df_sorted['PREV_TS_PCT'] = df_sorted.groupby('PLAYER_NAME')['TS_PCT'].shift(1)
    df_sorted['PREV_USG_RATE'] = df_sorted.groupby('PLAYER_NAME')['USG_RATE'].shift(1)
    
    # Calculate improvements
    df_sorted['PTS_IMPROVEMENT'] = df_sorted['PTS'] - df_sorted['PREV_PTS']
    df_sorted['TS_IMPROVEMENT'] = df_sorted['TS_PCT'] - df_sorted['PREV_TS_PCT']
    df_sorted['USG_IMPROVEMENT'] = df_sorted['USG_RATE'] - df_sorted['PREV_USG_RATE']
    
    # Overall improvement score
    df_sorted['OVERALL_IMPROVEMENT'] = (
        df_sorted['PTS_IMPROVEMENT'].fillna(0) * 0.4 +
        df_sorted['TS_IMPROVEMENT'].fillna(0) * 100 * 0.3 +
        df_sorted['USG_IMPROVEMENT'].fillna(0) * 0.3
    )
    
    return df_sorted

def identify_breakout_candidates(df):
    """Identify players likely to break out"""
    # Focus on players 21-25 years old
    young_df = df[(df['SEASON'] == '2023-24') & (df['AGE'].between(21, 25))]
    
    # Criteria for breakout potential
    breakout_criteria = (
        (young_df['MIN'] >= 15) &  # Getting decent minutes
        (young_df['TS_PCT'] >= 0.52) &  # Efficient shooter
        (young_df['USG_RATE'] <= 25) &  # Not yet primary option
        (young_df['DEV_SCORE'] >= 5)  # Good development metrics
    )
    
    candidates = young_df[breakout_criteria].copy()
    
    # Calculate breakout probability
    candidates['BREAKOUT_PROB'] = (
        candidates['TS_PCT'] * 0.3 +
        (30 - candidates['USG_RATE']) / 30 * 0.3 +
        candidates['DEV_SCORE'] / 10 * 0.4
    )
    
    return candidates.sort_values('BREAKOUT_PROB', ascending=False)

def process_development_data():
    """Main processing function"""
    # Load data
    historical = pd.read_csv('data/historical_player_data.csv')
    current = pd.read_csv('data/current_season_players.csv')
    
    # Calculate improvements
    historical_with_improvement = calculate_year_over_year_improvement(historical)
    
    # Identify breakout candidates
    breakout_candidates = identify_breakout_candidates(historical)
    
    # Create database and save
    conn = create_development_database()
    
    # Save to database
    historical_with_improvement.to_sql('player_development', conn, if_exists='replace', index=False)
    breakout_candidates.to_sql('breakout_candidates', conn, if_exists='replace', index=False)
    
    print("Data processing complete!")
    print(f"Found {len(breakout_candidates)} potential breakout candidates")
    
    return historical_with_improvement, breakout_candidates

if __name__ == "__main__":
    historical_data, candidates = process_development_data()
    
    # Show top 10 breakout candidates
    print("\nTop 10 Breakout Candidates:")
    print(candidates[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'AGE', 'PTS', 'TS_PCT', 'BREAKOUT_PROB']].head(10))