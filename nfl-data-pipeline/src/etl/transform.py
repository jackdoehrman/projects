"""
NFL Data Transformation Module

"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Tuple, Dict, List
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFLDataTransformer:
    """
    Handles all data cleaning and transformation operations for NFL data.
    
    """
    
    def __init__(self):
        self.raw_data_path = 'data/raw'
        self.processed_data_path = 'data/processed'
        
        # Ensure processed directory exists
        os.makedirs(self.processed_data_path, exist_ok=True)
        
    def load_raw_data(self, filename: str) -> pd.DataFrame:
        """
        Load raw data from CSV with error handling.

        """
        filepath = os.path.join(self.raw_data_path, filename)
        
        try:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"Loaded {len(df)} records from {filename}")
                return df
            else:
                logger.warning(f"File not found: {filepath}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    
    def clean_teams_data(self, teams_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate NFL teams data.

        """
        if teams_df.empty:
            logger.warning("No teams data to clean")
            return pd.DataFrame()
        
        logger.info("Cleaning teams data...")
        original_count = len(teams_df)
        
        # Removes duplicates based on team identifier
        id_columns = ['TeamID', 'team_id', 'Key']
        id_column = None
        
        for col in id_columns:
            if col in teams_df.columns:
                id_column = col
                break
        
        if id_column:
            teams_df = teams_df.drop_duplicates(subset=[id_column])
            logger.info(f"Removed {original_count - len(teams_df)} duplicate teams")
        
        # Standardizes column names to match our database schema
        column_mapping = {
            'TeamID': 'team_id',
            'Name': 'name',
            'City': 'city', 
            'Key': 'abbreviation',
            'Conference': 'conference',
            'Division': 'division',
            'PrimaryColor': 'primary_color',
            'SecondaryColor': 'secondary_color',
            'WikipediaLogoUrl': 'logo_url',
            'Founded': 'founded_year',
            'HeadCoach': 'head_coach'
        }
        
        # Renames columns that exist
        rename_map = {}
        for old_col, new_col in column_mapping.items():
            if old_col in teams_df.columns:
                rename_map[old_col] = new_col
        
        teams_df = teams_df.rename(columns=rename_map)
        
        # Handles missing values
        if 'city' in teams_df.columns:
            teams_df['city'] = teams_df['city'].fillna('Unknown')
        if 'conference' in teams_df.columns:
            teams_df['conference'] = teams_df['conference'].fillna('Unknown')
        if 'division' in teams_df.columns:
            teams_df['division'] = teams_df['division'].fillna('Unknown')
        
        # Standardizes text fields
        text_columns = ['name', 'city', 'abbreviation', 'conference', 'division']
        for col in text_columns:
            if col in teams_df.columns:
                teams_df[col] = teams_df[col].astype(str).str.strip()
        
        # Validates conference values
        if 'conference' in teams_df.columns:
            valid_conferences = ['AFC', 'NFC']
            invalid_conferences = ~teams_df['conference'].isin(valid_conferences + ['Unknown'])
            if invalid_conferences.any():
                logger.warning(f"Found {invalid_conferences.sum()} teams with invalid conferences")
                teams_df.loc[invalid_conferences, 'conference'] = 'Unknown'
        
        # Ensures team_id is integer
        if 'team_id' in teams_df.columns:
            teams_df['team_id'] = pd.to_numeric(teams_df['team_id'], errors='coerce')
            teams_df = teams_df.dropna(subset=['team_id'])
            teams_df['team_id'] = teams_df['team_id'].astype(int)
        
        logger.info(f"Teams data cleaning completed: {len(teams_df)} clean records")
        return teams_df
    
    def clean_games_data(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate NFL games data.

        """
        if games_df.empty:
            logger.warning("No games data to clean")
            return pd.DataFrame()
        
        logger.info("Cleaning games data...")
        original_count = len(games_df)
        
        # Standardizes column names
        column_mapping = {
            'GameID': 'game_id',
            'Season': 'season',
            'SeasonType': 'season_type',
            'Week': 'week',
            'Date': 'date',
            'DateTime': 'datetime',
            'HomeTeamID': 'home_team_id',
            'AwayTeamID': 'away_team_id',
            'HomeScore': 'home_score',
            'AwayScore': 'away_score',
            'Status': 'status',
            'Quarter': 'quarter',
            'TimeRemainingMinutes': 'time_remaining',
            'Temperature': 'weather_temperature',
            'WindSpeed': 'wind_speed'
        }
        
        # Renames columns that exist
        rename_map = {}
        for old_col, new_col in column_mapping.items():
            if old_col in games_df.columns:
                rename_map[old_col] = new_col
        
        games_df = games_df.rename(columns=rename_map)
        
        # Removes duplicates based on game_id
        if 'game_id' in games_df.columns:
            games_df = games_df.drop_duplicates(subset=['game_id'])
            logger.info(f"Removed {original_count - len(games_df)} duplicate games")
        
        # Handles missing scores (for future/scheduled games)
        score_columns = ['home_score', 'away_score']
        for col in score_columns:
            if col in games_df.columns:
                games_df[col] = pd.to_numeric(games_df[col], errors='coerce').fillna(0)
        
        # Cleans/validates date column
        if 'date' in games_df.columns:
            games_df['date'] = pd.to_datetime(games_df['date'], errors='coerce')
            # Remove games with invalid dates
            games_df = games_df.dropna(subset=['date'])
            # Convert to date (remove time component)
            games_df['date'] = games_df['date'].dt.date
        
        # Ensures numeric columns are proper types
        numeric_columns = ['season', 'week', 'home_team_id', 'away_team_id']
        for col in numeric_columns:
            if col in games_df.columns:
                games_df[col] = pd.to_numeric(games_df[col], errors='coerce')
        
        # Validates business rules
        if 'home_team_id' in games_df.columns and 'away_team_id' in games_df.columns:
            # Removes games where team plays itself (data error)
            same_team_games = games_df['home_team_id'] == games_df['away_team_id']
            if same_team_games.any():
                logger.warning(f"Removing {same_team_games.sum()} games where team plays itself")
                games_df = games_df[~same_team_games]
        
        # Validates week numbers (1-18 for regular season, 1-4 for playoffs)
        if 'week' in games_df.columns:
            invalid_weeks = (games_df['week'] < 1) | (games_df['week'] > 22)
            if invalid_weeks.any():
                logger.warning(f"Found {invalid_weeks.sum()} games with invalid week numbers")
                games_df = games_df[~invalid_weeks]
        
        logger.info(f"Games data cleaning completed: {len(games_df)} clean records")
        return games_df
    
    def create_game_features(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional analytical features from games data.
        
        """
        if games_df.empty:
            logger.warning("No games data for feature engineering")
            return pd.DataFrame()
        
        logger.info("Creating game features...")
        
        # Calculates point differential (positive = home team won)
        if 'home_score' in games_df.columns and 'away_score' in games_df.columns:
            games_df['point_differential'] = games_df['home_score'] - games_df['away_score']
            
            # Determines winner
            games_df['winner_team_id'] = np.where(
                games_df['home_score'] > games_df['away_score'],
                games_df['home_team_id'],  # Home team won
                np.where(
                    games_df['away_score'] > games_df['home_score'],
                    games_df['away_team_id'],  # Away team won
                    None  # Tie game (rare in NFL)
                )
            )
            
            # Calculates absolute margin of victory
            games_df['margin_of_victory'] = abs(games_df['point_differential'])
            
            # Categorizes game closeness
            games_df['game_closeness'] = pd.cut(
                games_df['margin_of_victory'],
                bins=[0, 3, 7, 14, float('inf')],
                labels=['Very Close (1-3)', 'Close (4-7)', 'Moderate (8-14)', 'Blowout (15+)'],
                include_lowest=True
            )
        
        # Creates game completion flag
        if 'status' in games_df.columns:
            completed_statuses = ['Final', 'F', 'Completed']
            games_df['is_completed'] = games_df['status'].isin(completed_statuses)
        
        # Extracts temporal features from date
        if 'date' in games_df.columns:
            # Converts to datetime if it's not already
            if games_df['date'].dtype == 'object':
                games_df['date'] = pd.to_datetime(games_df['date'])
            
            games_df['year'] = games_df['date'].dt.year
            games_df['month'] = games_df['date'].dt.month
            games_df['day_of_week'] = games_df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
            games_df['day_name'] = games_df['date'].dt.day_name()
            
            # NFL typically plays on Sunday (6), Monday (0), Thursday (3)
            games_df['is_prime_time'] = games_df['day_of_week'].isin([0, 3])  # Monday/Thursday
            games_df['is_sunday'] = games_df['day_of_week'] == 6
        
        # Calculates total points for over/under analysis
        if 'home_score' in games_df.columns and 'away_score' in games_df.columns:
            games_df['total_points'] = games_df['home_score'] + games_df['away_score']
            
            # Categorizes scoring games
            games_df['scoring_category'] = pd.cut(
                games_df['total_points'],
                bins=[0, 35, 45, 55, float('inf')],
                labels=['Low Scoring (≤35)', 'Average (36-45)', 'High (46-55)', 'Very High (56+)'],
                include_lowest=True
            )
        
        logger.info(f"Feature engineering completed: {len(games_df.columns)} total columns")
        return games_df
    
    def create_team_aggregations(self, games_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create team-level performance aggregations.
        
        """
        if games_df.empty:
            logger.warning("No games data for team aggregations")
            return pd.DataFrame()
        
        logger.info("Creating team aggregations...")
        
        # Filters to completed games only
        if 'is_completed' in games_df.columns:
            completed_games = games_df[games_df['is_completed'] == True].copy()
        else:
            # Fallback: use games with scores > 0
            completed_games = games_df[
                (games_df['home_score'] > 0) | (games_df['away_score'] > 0)
            ].copy()
        
        if completed_games.empty:
            logger.warning("No completed games found for aggregations")
            return pd.DataFrame()
        
        # Home team stats
        home_stats = completed_games.groupby('home_team_id').agg({
            'game_id': 'count',  # Home games played
            'home_score': ['mean', 'sum', 'std'],  # Home scoring stats
            'away_score': 'mean',  # Points allowed at home
            'point_differential': 'mean'  # Home point differential
        }).reset_index()
        
        # Flattens column names
        home_stats.columns = [
            'team_id', 'home_games', 'avg_points_scored_home', 
            'total_points_home', 'std_points_home', 'avg_points_allowed_home', 
            'avg_differential_home'
        ]
        
        # Calculates home wins
        home_wins = completed_games[completed_games['home_score'] > completed_games['away_score']].groupby('home_team_id').size().reset_index(name='home_wins')
        home_stats = home_stats.merge(home_wins, on='team_id', how='left')
        home_stats['home_wins'] = home_stats['home_wins'].fillna(0)
        
        # Away team stats
        away_stats = completed_games.groupby('away_team_id').agg({
            'game_id': 'count',  # Away games played
            'away_score': ['mean', 'sum', 'std'],  # Away scoring stats
            'home_score': 'mean',  # Points allowed on road
            'point_differential': lambda x: -x.mean()  # Away perspective (flip sign)
        }).reset_index()
        
        # Flattens column names
        away_stats.columns = [
            'team_id', 'away_games', 'avg_points_scored_away', 
            'total_points_away', 'std_points_away', 'avg_points_allowed_away', 
            'avg_differential_away'
        ]
        
        # Calculates away wins
        away_wins = completed_games[completed_games['away_score'] > completed_games['home_score']].groupby('away_team_id').size().reset_index(name='away_wins')
        away_stats = away_stats.merge(away_wins, on='team_id', how='left')
        away_stats['away_wins'] = away_stats['away_wins'].fillna(0)
        
        # Combines home and away stats
        team_stats = home_stats.merge(away_stats, on='team_id', how='outer')
        team_stats = team_stats.fillna(0)
        
        # Calculates overall stats
        team_stats['total_games'] = team_stats['home_games'] + team_stats['away_games']
        team_stats['total_wins'] = team_stats['home_wins'] + team_stats['away_wins']
        team_stats['total_losses'] = team_stats['total_games'] - team_stats['total_wins']
        team_stats['win_percentage'] = team_stats['total_wins'] / team_stats['total_games'].replace(0, 1)
        
        # Calculates weighted averages for overall performance
        team_stats['avg_points_scored'] = (
            (team_stats['avg_points_scored_home'] * team_stats['home_games'] + 
             team_stats['avg_points_scored_away'] * team_stats['away_games']) / 
            team_stats['total_games'].replace(0, 1)
        )
        
        team_stats['avg_points_allowed'] = (
            (team_stats['avg_points_allowed_home'] * team_stats['home_games'] + 
             team_stats['avg_points_allowed_away'] * team_stats['away_games']) / 
            team_stats['total_games'].replace(0, 1)
        )
        
        # Calculates net points and efficiency metrics
        team_stats['net_points'] = team_stats['avg_points_scored'] - team_stats['avg_points_allowed']
        team_stats['home_field_advantage'] = team_stats['avg_differential_home'] - team_stats['avg_differential_away']
        
        # Ranks teams by performance
        team_stats = team_stats.sort_values(['win_percentage', 'net_points'], ascending=[False, False])
        team_stats['power_ranking'] = range(1, len(team_stats) + 1)
        
        logger.info(f"Team aggregations completed: {len(team_stats)} teams analyzed")
        return team_stats
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """
        Save data to CSV.

        """
        if df.empty:
            logger.warning(f"No data to save for {filename}")
            return
        
        try:
            filepath = os.path.join(self.processed_data_path, filename)
            df.to_csv(filepath, index=False)
            
            logger.info(f"Saved {len(df)} processed records to {filepath}")
            
            # Logs column information for verification
            logger.info(f"Columns in {filename}: {df.columns.tolist()}")
            
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")

# Tests transformations
if __name__ == "__main__":
    """
    Standalone script for testing data transformations.
    """
    logger.info("Starting NFL data transformation...")
    
    transformer = NFLDataTransformer()
    
    # Transforms teams data
    logger.info("=== Transforming Teams Data ===")
    teams_df = transformer.load_raw_data('nfl_teams_test.csv')
    if not teams_df.empty:
        clean_teams = transformer.clean_teams_data(teams_df)
        transformer.save_processed_data(clean_teams, 'nfl_teams_clean.csv')
        logger.info(f"Teams transformation completed: {len(clean_teams)} teams")
    
    # Transforms games data (if available)
    logger.info("=== Transforming Games Data ===")
    games_df = transformer.load_raw_data('nfl_games_2024.csv')
    if not games_df.empty:
        clean_games = transformer.clean_games_data(games_df)
        games_with_features = transformer.create_game_features(clean_games)
        transformer.save_processed_data(games_with_features, 'nfl_games_clean.csv')
        
        # Creates team aggregations
        team_stats = transformer.create_team_aggregations(games_with_features)
        transformer.save_processed_data(team_stats, 'nfl_team_stats.csv')
        
        logger.info(f"Games transformation completed: {len(games_with_features)} games")
        logger.info(f"Team stats created: {len(team_stats)} teams")
    
    logger.info("Data transformation completed!")