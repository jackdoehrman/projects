"""
NFL Data Extraction Module

"""

import requests
import pandas as pd
import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

# Sets up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFLDataExtractor:
    """
    Handle extraction of NFL data.

    """
    
    def __init__(self, api_key: str):
        """
        Initialize extractor w/ API credentials. Provided by SportsDataIO.
        
        """
        self.api_key = api_key
        self.base_url = "https://api.sportsdata.io/v3/nfl"
        
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "User-Agent": "NFL-Data-Pipeline/1.0"
        }
        
        # Limits API rate
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Min 1 second between requests
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:

        # Implements rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: sleeping {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"Making request to: {endpoint}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            self.last_request_time = time.time()
            
            # Checks for errors
            response.raise_for_status()
            
            # Validates response content
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Unexpected status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from {endpoint}: {e}")
            return None
    
    def get_teams(self) -> pd.DataFrame:
        """
        Extract NFL team data.

        """
        logger.info("Extracting NFL teams data...")
        
        # teams endpoint
        data = self._make_request("scores/json/teams")
        
        if not data:
            logger.error("Failed to fetch teams data")
            return pd.DataFrame()
        
        try:
            # Converts JSON to DataFrame
            teams_df = pd.DataFrame(data)
            
            if teams_df.empty:
                logger.warning("No teams data returned from API")
                return pd.DataFrame()
            
            # Logs raw data structure for debugging
            logger.info(f"Raw teams data columns: {teams_df.columns.tolist()}")
            
            # Maps API fields to database schema
            column_mapping = {
                'TeamID': 'team_id',
                'Name': 'name', 
                'City': 'city',
                'Key': 'abbreviation',  # Team abbreviation (DAL, NE, etc.)
                'Conference': 'conference',
                'Division': 'division',
                'PrimaryColor': 'primary_color',
                'SecondaryColor': 'secondary_color',
                'WikipediaLogoUrl': 'logo_url',
                'Founded': 'founded_year',
                'StadiumDetails': 'stadium_name',
                'HeadCoach': 'head_coach'
            }
            
            # Selects and renames columns that exist in the API response
            available_columns = {}
            for api_col, db_col in column_mapping.items():
                if api_col in teams_df.columns:
                    available_columns[api_col] = db_col
                else:
                    logger.warning(f"Column {api_col} not found in API response")
            
            # Selects available columns and rename
            if available_columns:
                teams_df = teams_df[list(available_columns.keys())].rename(columns=available_columns)
            else:
                logger.error("No expected columns found in teams data")
                return pd.DataFrame()
            
            # Data validation/cleaning
            if 'team_id' in teams_df.columns:
                teams_df = teams_df.dropna(subset=['team_id'])  # Must have team ID
                teams_df['team_id'] = teams_df['team_id'].astype(int)
            
            # Cleans text fields
            text_columns = ['name', 'city', 'abbreviation']
            for col in text_columns:
                if col in teams_df.columns:
                    teams_df[col] = teams_df[col].astype(str).str.strip()
            
            logger.info(f"Successfully extracted {len(teams_df)} teams")
            return teams_df
            
        except Exception as e:
            logger.error(f"Error processing teams data: {e}")
            return pd.DataFrame()
    
    def get_games(self, season: str = "2024", season_type: str = "REG") -> pd.DataFrame:
        """
        Extract NFL games data for a specific season.
        
        """
        logger.info(f"Extracting NFL games for {season} {season_type} season...")
        
        # Constructs endpoint for specific season
        endpoint = f"scores/json/Games/{season}{season_type}"
        data = self._make_request(endpoint)
        
        if not data:
            logger.error(f"Failed to fetch games data for {season}")
            return pd.DataFrame()
        
        try:
            games_df = pd.DataFrame(data)
            
            if games_df.empty:
                logger.warning(f"No games data returned for {season}")
                return pd.DataFrame()
            
            logger.info(f"Raw games data columns: {games_df.columns.tolist()}")
            
            # Maps API fields to database schema
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
                'StadiumDetails': 'stadium',
                'Temperature': 'weather_temperature',
                'WindSpeed': 'wind_speed'
            }
            
            # Selects and renames available columns
            available_columns = {}
            for api_col, db_col in column_mapping.items():
                if api_col in games_df.columns:
                    available_columns[api_col] = db_col
            
            if available_columns:
                games_df = games_df[list(available_columns.keys())].rename(columns=available_columns)
            else:
                logger.error("No expected columns found in games data")
                return pd.DataFrame()
            
            # Data cleaning/validation
            if 'game_id' in games_df.columns:
                games_df = games_df.dropna(subset=['game_id'])
                games_df['game_id'] = games_df['game_id'].astype(int)
            
            # Date formatting
            if 'date' in games_df.columns:
                games_df['date'] = pd.to_datetime(games_df['date'], errors='coerce').dt.date
            
            # Cleans numeric fields
            numeric_columns = ['home_score', 'away_score', 'week', 'season']
            for col in numeric_columns:
                if col in games_df.columns:
                    games_df[col] = pd.to_numeric(games_df[col], errors='coerce').fillna(0)
            
            # Filters out invalid games
            games_df = games_df.dropna(subset=['date'])
            
            logger.info(f"Successfully extracted {len(games_df)} games")
            return games_df
            
        except Exception as e:
            logger.error(f"Error processing games data: {e}")
            return pd.DataFrame()
    
    def save_raw_data(self, df: pd.DataFrame, filename: str):
        """
        Save raw data to CSV.

        """
        if df.empty:
            logger.warning(f"No data to save for {filename}")
            return
        
        try:
            # Makes sure directory exists
            os.makedirs('data/raw', exist_ok=True)
            
            filepath = f'data/raw/{filename}'
            df.to_csv(filepath, index=False)
            
            logger.info(f"Saved {len(df)} records to {filepath}")
            
            # Logs sample for verification
            logger.info(f"Sample data from {filename}:")
            logger.info(f"Columns: {df.columns.tolist()}")
            if len(df) > 0:
                logger.info(f"First row: {df.iloc[0].to_dict()}")
                
        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")

# Command-line interface for testing
if __name__ == "__main__":
    
    # Gets API key from environment variable
    api_key = os.getenv('NFL_API_KEY') or os.getenv('SPORTS_API_KEY')
    
    if not api_key:
        logger.error("API key not found. Set NFL_API_KEY or SPORTS_API_KEY environment variable.")
        logger.info("Get your free API key from: https://sportsdata.io/")
        exit(1)
    
    # Initializes extractor
    extractor = NFLDataExtractor(api_key)
    
    # Extracts teams data
    logger.info("=== Extracting Teams Data ===")
    teams_df = extractor.get_teams()
    if not teams_df.empty:
        extractor.save_raw_data(teams_df, 'nfl_teams.csv')
        logger.info(f"Teams extraction completed: {len(teams_df)} teams")
    
    # Extracts current season games
    logger.info("=== Extracting Games Data ===")
    games_df = extractor.get_games(season="2024", season_type="REG")
    if not games_df.empty:
        extractor.save_raw_data(games_df, 'nfl_games_2024.csv')
        logger.info(f"Games extraction completed: {len(games_df)} games")
    
    logger.info("Data extraction completed!")