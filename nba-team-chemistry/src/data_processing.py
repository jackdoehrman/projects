import pandas as pd
import sqlite3
import numpy as np

def create_chemistry_database():
    """Set up database for team chemistry analytics"""
    conn = sqlite3.connect('data/nba_chemistry.db')
    
    # Team performance table (updated for real data structure)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS team_performance (
        team_id INTEGER,
        team_name TEXT,
        team_abbreviation TEXT,
        games_played INTEGER,
        wins INTEGER,
        losses INTEGER,
        win_pct REAL,
        minutes REAL,
        points REAL,
        plus_minus REAL,
        fg_pct REAL,
        fg3_pct REAL,
        offensive_rating REAL,
        defensive_rating REAL,
        net_rating REAL,
        pace REAL,
        chemistry_rating TEXT
    )
    ''')
    
    # Player chemistry table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS player_chemistry (
        player_name TEXT,
        team_abbreviation TEXT,
        minutes REAL,
        points REAL,
        assists REAL,
        rebounds REAL,
        plus_minus REAL,
        efficiency_score REAL
    )
    ''')
    
    return conn

def calculate_advanced_metrics(lineup_df):
    """Calculate team chemistry metrics from available data"""
    
    # Calculate offensive and defensive ratings (approximations)
    # NBA uses possessions, but we'll approximate
    lineup_df['POSSESSIONS'] = lineup_df['FGA'] + 0.44 * lineup_df['FTA'] + lineup_df['TOV']
    
    # Offensive Rating = Points per 100 possessions
    lineup_df['OFFENSIVE_RATING'] = (lineup_df['PTS'] / lineup_df['POSSESSIONS']) * 100
    
    # Defensive Rating (approximation - inverse of efficiency)
    lineup_df['DEFENSIVE_RATING'] = 110 - (lineup_df['PLUS_MINUS'] / lineup_df['GP'])
    
    # Net Rating
    lineup_df['NET_RATING'] = lineup_df['OFFENSIVE_RATING'] - lineup_df['DEFENSIVE_RATING']
    
    # Pace (approximation)
    lineup_df['PACE'] = (lineup_df['POSSESSIONS'] / lineup_df['MIN']) * 48
    
    # Team Chemistry Score (custom metric)
    lineup_df['CHEMISTRY_SCORE'] = (
        lineup_df['W_PCT'] * 30 +  # Winning percentage
        lineup_df['NET_RATING'] * 0.5 +  # Net rating impact
        (lineup_df['AST'] / lineup_df['TOV']) * 5  # Ball movement efficiency
    )
    
    return lineup_df

def analyze_team_chemistry(lineup_df):
    """Analyze team chemistry based on performance metrics"""
    
    # Classify chemistry levels based on multiple factors
    def classify_chemistry(row):
        score = 0
        
        # Win percentage factor
        if row['W_PCT'] >= 0.60:
            score += 3
        elif row['W_PCT'] >= 0.50:
            score += 2
        elif row['W_PCT'] >= 0.40:
            score += 1
        
        # Plus/minus factor
        if row['PLUS_MINUS'] > 100:
            score += 2
        elif row['PLUS_MINUS'] > 0:
            score += 1
        
        # Ball movement (assists vs turnovers)
        ast_tov_ratio = row['AST'] / max(row['TOV'], 1)
        if ast_tov_ratio >= 2.0:
            score += 2
        elif ast_tov_ratio >= 1.5:
            score += 1
        
        # Classify based on total score
        if score >= 6:
            return 'Elite Chemistry'
        elif score >= 4:
            return 'Good Chemistry'
        elif score >= 2:
            return 'Average Chemistry'
        else:
            return 'Poor Chemistry'
    
    lineup_df['CHEMISTRY_RATING'] = lineup_df.apply(classify_chemistry, axis=1)
    
    return lineup_df

def analyze_team_strengths(lineup_df):
    """Identify each team's strengths and weaknesses"""
    
    team_analysis = []
    
    for _, team in lineup_df.iterrows():
        strengths = []
        weaknesses = []
        
        # Offensive analysis
        if team['FG_PCT'] >= 0.47:
            strengths.append('Efficient Shooting')
        elif team['FG_PCT'] <= 0.43:
            weaknesses.append('Poor Shooting')
            
        if team['FG3_PCT'] >= 0.36:
            strengths.append('3-Point Shooting')
        elif team['FG3_PCT'] <= 0.32:
            weaknesses.append('3-Point Struggles')
            
        # Ball movement
        ast_tov_ratio = team['AST'] / max(team['TOV'], 1)
        if ast_tov_ratio >= 2.0:
            strengths.append('Ball Movement')
        elif ast_tov_ratio <= 1.3:
            weaknesses.append('Turnovers')
            
        # Rebounding
        if team['REB'] >= 45:
            strengths.append('Rebounding')
        elif team['REB'] <= 40:
            weaknesses.append('Rebounding')
        
        team_analysis.append({
            'team_name': team['TEAM_NAME'],
            'team_abbreviation': team['TEAM_ABBREVIATION'],
            'strengths': ', '.join(strengths) if strengths else 'None Identified',
            'weaknesses': ', '.join(weaknesses) if weaknesses else 'None Identified',
            'chemistry_rating': team['CHEMISTRY_RATING'],
            'overall_score': team['CHEMISTRY_SCORE']
        })
    
    return pd.DataFrame(team_analysis)

def process_chemistry_data():
    """Main processing function"""
    
    # Load data
    lineup_data = pd.read_csv('data/team_lineups.csv')
    player_data = pd.read_csv('data/player_chemistry.csv')
    
    print("Processing team chemistry data...")
    print(f"Teams to analyze: {len(lineup_data)}")
    
    # Calculate advanced metrics
    lineup_with_metrics = calculate_advanced_metrics(lineup_data)
    
    # Analyze chemistry
    lineup_with_chemistry = analyze_team_chemistry(lineup_with_metrics)
    
    # Team strengths analysis
    team_strengths = analyze_team_strengths(lineup_with_chemistry)
    
    # Create database and save
    conn = create_chemistry_database()
    
    # Save to database
    lineup_with_chemistry.to_sql('team_performance', conn, if_exists='replace', index=False)
    player_data.to_sql('player_chemistry', conn, if_exists='replace', index=False)
    
    print("Data processing complete!")
    print(f"Analyzed {len(lineup_with_chemistry)} teams")
    
    return lineup_with_chemistry, team_strengths, player_data

if __name__ == "__main__":
    team_data, strengths, players = process_chemistry_data()
    
    # Show results
    print("\nTeam Chemistry Analysis:")
    print("=" * 50)
    
    for _, team in team_data.iterrows():
        print(f"{team['TEAM_NAME']} ({team['TEAM_ABBREVIATION']}):")
        print(f"  Record: {team['W']}-{team['L']} ({team['W_PCT']:.3f})")
        print(f"  Plus/Minus: {team['PLUS_MINUS']:+.0f}")
        print(f"  Chemistry: {team['CHEMISTRY_RATING']}")
        print(f"  Net Rating: {team['NET_RATING']:+.1f}")
        print()
    
    if not strengths.empty:
        print("Team Strengths & Weaknesses:")
        print("=" * 30)
        for _, analysis in strengths.iterrows():
            print(f"{analysis['team_name']}:")
            print(f"  Strengths: {analysis['strengths']}")
            print(f"  Weaknesses: {analysis['weaknesses']}")
            print()