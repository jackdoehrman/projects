import sqlite3
import pandas as pd

conn = sqlite3.connect('data/nba_development.db')

# Test the queries
queries = {
    "Top Players by Age Group": """
    SELECT 
        CASE 
            WHEN AGE <= 22 THEN 'Young (≤22)'
            WHEN AGE <= 25 THEN 'Prime Development (23-25)'
            ELSE 'Veteran (26+)'
        END as age_group,
        PLAYER_NAME,
        AGE,
        PTS,
        TS_PCT
    FROM player_development 
    WHERE SEASON = '2023-24'
    ORDER BY age_group, PTS DESC;
    """,
    
    "Breakout Candidates": """
    SELECT 
        PLAYER_NAME,
        TEAM_ABBREVIATION as team,
        AGE,
        ROUND(PTS, 1) as ppg,
        ROUND(TS_PCT, 3) as ts_pct,
        ROUND(BREAKOUT_PROB, 3) as breakout_probability
    FROM breakout_candidates 
    ORDER BY BREAKOUT_PROB DESC;
    """
}

for query_name, query in queries.items():
    print(f"\n{query_name}:")
    print("=" * 40)
    try:
        result = pd.read_sql(query, conn)
        print(result.head())
    except Exception as e:
        print(f"Error: {e}")

conn.close()