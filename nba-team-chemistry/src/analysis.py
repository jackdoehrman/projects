import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import numpy as np

def run_chemistry_analysis():
    """Complete NBA team chemistry analysis"""
    
    # Load data
    conn = sqlite3.connect('data/nba_chemistry.db')
    team_data = pd.read_sql('SELECT * FROM team_performance', conn)
    player_data = pd.read_sql('SELECT * FROM player_chemistry', conn)
    
    print("NBA TEAM CHEMISTRY ANALYSIS")
    print("=" * 50)
    print(f"Teams analyzed: {len(team_data)}")
    print(f"Players analyzed: {len(player_data)}")
    
    # Team Chemistry Analysis
    print("\nTEAM CHEMISTRY RANKINGS:")
    print("-" * 30)
    
    # Sort by chemistry score
    top_chemistry = team_data.sort_values('CHEMISTRY_SCORE', ascending=False)
    
    for _, team in top_chemistry.iterrows():
        print(f"{team['TEAM_NAME']}:")
        print(f"  Chemistry Rating: {team['CHEMISTRY_RATING']}")
        print(f"  Record: {team['wins']}-{team['losses']} ({team['W_PCT']:.3f})")
        print(f"  Net Rating: {team['net_rating']:+.1f}")
        print(f"  Plus/Minus: {team['plus_minus']:+.0f}")
        print()
    
    # Key Insights
    print("KEY INSIGHTS:")
    print("-" * 15)
    
    # Best shooting team
    best_fg = team_data.loc[team_data['FG_PCT'].idxmax()]
    print(f"Best Shooting: {best_fg['TEAM_NAME']} ({best_fg['FG_PCT']:.3f} FG%)")
    
    # Best 3-point shooting
    best_3pt = team_data.loc[team_data['FG3_PCT'].idxmax()]
    print(f"Best 3-Point: {best_3pt['TEAM_NAME']} ({best_3pt['FG3_PCT']:.3f} 3P%)")
    
    # Best ball movement (AST/TOV ratio)
    team_data['AST_TOV_RATIO'] = team_data['AST'] / team_data['TOV']
    best_passing = team_data.loc[team_data['AST_TOV_RATIO'].idxmax()]
    print(f"Best Ball Movement: {best_passing['TEAM_NAME']} ({best_passing['AST_TOV_RATIO']:.2f} AST/TOV)")
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Win % vs Chemistry Score
    axes[0,0].scatter(team_data['W_PCT'], team_data['CHEMISTRY_SCORE'], s=100, alpha=0.7)
    axes[0,0].set_xlabel('Win Percentage')
    axes[0,0].set_ylabel('Chemistry Score')
    axes[0,0].set_title('Win % vs Team Chemistry')
    
    # Add team labels
    for _, team in team_data.iterrows():
        axes[0,0].annotate(team['TEAM_ABBREVIATION'], 
                          (team['W_PCT'], team['CHEMISTRY_SCORE']),
                          xytext=(5, 5), textcoords='offset points')
    
    # Offensive vs Defensive Rating
    axes[0,1].scatter(team_data['DEFENSIVE_RATING'], team_data['OFFENSIVE_RATING'], 
                     s=team_data['wins']*3, alpha=0.7)
    axes[0,1].set_xlabel('Defensive Rating (Lower is Better)')
    axes[0,1].set_ylabel('Offensive Rating (Higher is Better)')
    axes[0,1].set_title('Offensive vs Defensive Efficiency')
    
    # Shooting Efficiency
    shooting_metrics = ['FG_PCT', 'FG3_PCT']
    team_shooting = team_data[['TEAM_ABBREVIATION'] + shooting_metrics].set_index('TEAM_ABBREVIATION')
    team_shooting.plot(kind='bar', ax=axes[1,0])
    axes[1,0].set_title('Shooting Efficiency by Team')
    axes[1,0].set_ylabel('Shooting Percentage')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Plus/Minus Distribution
    team_data['plus_minus'].hist(bins=10, ax=axes[1,1], alpha=0.7)
    axes[1,1].set_title('Plus/Minus Distribution')
    axes[1,1].set_xlabel('Plus/Minus')
    axes[1,1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('data/nba_chemistry_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved as: data/nba_chemistry_analysis.png")
    plt.show()
    
    # Player Analysis (if available)
    if not player_data.empty:
        print(f"\nTOP PLAYERS BY PLUS/MINUS:")
        print("-" * 25)
        top_players = player_data.nlargest(5, 'plus_minus')
        for _, player in top_players.iterrows():
            print(f"{player['player_name']} ({player['team_abbreviation']}): {player['plus_minus']:+.0f}")
    
    conn.close()

if __name__ == "__main__":
    run_chemistry_analysis()