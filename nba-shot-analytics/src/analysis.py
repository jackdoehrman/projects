import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import numpy as np

def run_shot_analytics():
    """Complete NBA shot analytics analysis"""
    
    # Load data
    conn = sqlite3.connect('data/nba_shot_analytics.db')
    shot_data = pd.read_sql('SELECT * FROM shot_attempts', conn)
    player_data = pd.read_sql('SELECT * FROM player_shooting', conn)
    team_data = pd.read_sql('SELECT * FROM team_efficiency', conn)
    
    print("NBA SHOT ANALYTICS ANALYSIS")
    print("=" * 50)
    print(f"Total shot attempts: {len(shot_data)}")
    print(f"Players analyzed: {len(player_data)}")
    print(f"Teams analyzed: {len(team_data)}")
    
    # Shot Selection Analysis
    if not player_data.empty:
        print("\nSHOT SELECTION RANKINGS:")
        print("-" * 35)
        
        top_selection = player_data.sort_values('shot_selection_score', ascending=False)
        
        for _, player in top_selection.head().iterrows():
            print(f"{player['player_name']}:")
            print(f"  Selection Score: {player['shot_selection_score']:.1f}")
            print(f"  Overall FG%: {player['overall_fg_pct']:.3f}")
            print(f"  At Rim: {player['at_rim_attempts']} attempts ({player['at_rim_fg_pct']:.3f})")
            print(f"  3-Point: {player['three_point_attempts']} attempts ({player['three_point_pct']:.3f})")
            print(f"  Mid-Range: {player['midrange_attempts']} attempts ({player['midrange_fg_pct']:.3f})")
            print()
    
    # Team Efficiency Analysis
    if not team_data.empty:
        print("TEAM EFFICIENCY RANKINGS:")
        print("-" * 30)
        
        top_teams = team_data.sort_values('overall_efficiency_score', ascending=False)
        
        for _, team in top_teams.iterrows():
            print(f"{team['team_name']} ({team['team_abbreviation']}):")
            print(f"  Efficiency Score: {team['overall_efficiency_score']:.1f}")
            print(f"  Close Range%: {team['close_range_pct']:.3f}")
            print(f"  3-Point%: {team['three_point_pct']:.3f}")
            print()
    
    # Key Insights
    print("KEY INSIGHTS:")
    print("-" * 15)
    
    if not player_data.empty:
        # Best at rim shooter
        best_rim = player_data.loc[player_data['at_rim_fg_pct'].idxmax()]
        print(f"Best At Rim: {best_rim['player_name']} ({best_rim['at_rim_fg_pct']:.3f})")
        
        # Best 3-point shooter
        best_3pt = player_data.loc[player_data['three_point_pct'].idxmax()]
        print(f"Best 3-Point: {best_3pt['player_name']} ({best_3pt['three_point_pct']:.3f})")
        
        # Best shot selection
        best_selection = player_data.loc[player_data['shot_selection_score'].idxmax()]
        print(f"Best Selection: {best_selection['player_name']} ({best_selection['shot_selection_score']:.1f})")
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    if not player_data.empty:
        # Shot selection vs efficiency
        axes[0,0].scatter(player_data['shot_selection_score'], player_data['overall_fg_pct'], 
                         alpha=0.7, s=60)
        axes[0,0].set_xlabel('Shot Selection Score')
        axes[0,0].set_ylabel('Overall FG%')
        axes[0,0].set_title('Shot Selection vs Shooting Efficiency')
        
        # 3-point vs at-rim efficiency
        axes[0,1].scatter(player_data['at_rim_fg_pct'], player_data['three_point_pct'], 
                         alpha=0.7, s=60)
        axes[0,1].set_xlabel('At Rim FG%')
        axes[0,1].set_ylabel('3-Point FG%')
        axes[0,1].set_title('At Rim vs 3-Point Efficiency')
        
        # Shot distribution
        shot_types = ['At Rim', '3-Point', 'Mid-Range']
        avg_attempts = [
            player_data['at_rim_attempts'].mean(),
            player_data['three_point_attempts'].mean(),
            player_data['midrange_attempts'].mean()
        ]
        
        axes[1,0].bar(shot_types, avg_attempts, color=['#2E8B57', '#4169E1', '#FF6347'])
        axes[1,0].set_title('Average Shot Distribution')
        axes[1,0].set_ylabel('Average Attempts')
        axes[1,0].tick_params(axis='x', rotation=45)
    
    if not team_data.empty:
        # Team efficiency comparison
        axes[1,1].scatter(team_data['three_point_pct'], team_data['close_range_pct'], 
                         s=team_data['overall_efficiency_score']*3, alpha=0.7)
        axes[1,1].set_xlabel('3-Point Percentage')
        axes[1,1].set_ylabel('Close Range Percentage')
        axes[1,1].set_title('Team Shooting Efficiency (Size = Overall Score)')
        
        # Add team labels
        for _, team in team_data.iterrows():
            axes[1,1].annotate(team['team_abbreviation'], 
                              (team['three_point_pct'], team['close_range_pct']),
                              xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('data/nba_shot_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved as: data/nba_shot_analysis.png")
    plt.show()