-- NFL Data Warehouse Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Master list of all 32 NFL teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,                    -- Internal unique ID
    team_id INTEGER UNIQUE NOT NULL,          -- External team ID from API
    name VARCHAR(100) NOT NULL,               -- Team name
    city VARCHAR(50),                         -- Team city
    abbreviation VARCHAR(5),                  -- Team abbreviation
    conference VARCHAR(3) CHECK (conference IN ('AFC', 'NFC')), -- Conference
    division VARCHAR(20),                     -- Division
    primary_color VARCHAR(7),                 -- Hex Primary team color code
    secondary_color VARCHAR(7),               -- Hex Secondary team color code
    logo_url TEXT,                           -- URL to team logo image
    founded_year INTEGER,                    -- Year team was founded
    stadium_name VARCHAR(100),               -- Home stadium name
    stadium_capacity INTEGER,               -- Stadium seating capacity
    head_coach VARCHAR(100),                -- Current head coach
    created_at TIMESTAMP DEFAULT NOW(),     -- When record was inserted
    updated_at TIMESTAMP DEFAULT NOW()      -- When record was last updated
);

-- Individual NFL game results and details table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    game_id INTEGER UNIQUE NOT NULL,         -- External game ID from API
    season INTEGER NOT NULL,                 -- Season year
    season_type VARCHAR(20) DEFAULT 'REG',  -- REG, POST, PRE (time of season)
    week INTEGER,                           -- Week number
    date DATE NOT NULL,                     -- Game date
    time TIME,                              -- Game time
    home_team_id INTEGER REFERENCES teams(team_id), -- Foreign key to teams
    away_team_id INTEGER REFERENCES teams(team_id), -- Foreign key to teams
    home_score INTEGER DEFAULT 0,          -- Home team final score
    away_score INTEGER DEFAULT 0,          -- Away team final score
    
    -- Game status tracking
    status VARCHAR(20) DEFAULT 'Scheduled', -- Scheduled, InProgress, Final, Postponed
    quarter VARCHAR(10),                    -- Current quarter or 'Final'
    time_remaining VARCHAR(10),             -- Time left in current quarter
    
    -- Game conditions
    weather_temperature INTEGER,           -- Temperature in Fahrenheit
    weather_condition VARCHAR(50),         -- Clear, Rain, Snow, etc.
    wind_speed INTEGER,                    -- Wind speed in MPH
    stadium VARCHAR(100),                  -- Stadium where game was played
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints to ensure data quality
    CHECK (home_team_id != away_team_id),  -- Team can't play itself
    CHECK (week BETWEEN 1 AND 22),        -- Valid week range
    CHECK (season BETWEEN 1920 AND 2030)  -- Reasonable season range
);

-- Individual player performance per game table
CREATE TABLE IF NOT EXISTS player_stats (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(game_id),
    player_id INTEGER NOT NULL,            -- External player ID from API
    player_name VARCHAR(100) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id),
    position VARCHAR(5),

    -- Passing stats
    passing_attempts INTEGER DEFAULT 0,
    passing_completions INTEGER DEFAULT 0,
    passing_yards INTEGER DEFAULT 0,
    passing_touchdowns INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,

    -- Rushing stats
    rushing_attempts INTEGER DEFAULT 0,
    rushing_yards INTEGER DEFAULT 0,
    rushing_touchdowns INTEGER DEFAULT 0,
    fumbles INTEGER DEFAULT 0,

    -- Receiving stats
    receptions INTEGER DEFAULT 0,
    receiving_yards INTEGER DEFAULT 0,
    receiving_touchdowns INTEGER DEFAULT 0,
    targets INTEGER DEFAULT 0,

    -- Defense stats
    tackles INTEGER DEFAULT 0,
    sacks DECIMAL(3,1) DEFAULT 0,          -- Sacks can be fractional (0.5 sacks)
    defensive_interceptions INTEGER DEFAULT 0,
    fumbles_recovered INTEGER DEFAULT 0,

    -- Special teams stats
    field_goals_made INTEGER DEFAULT 0,
    field_goals_attempted INTEGER DEFAULT 0,
    extra_points_made INTEGER DEFAULT 0,
    extra_points_attempted INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Aggregated team performance by season table
CREATE TABLE IF NOT EXISTS team_season_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(team_id),
    season INTEGER NOT NULL,
    season_type VARCHAR(20) DEFAULT 'REG',
    
    -- Win/Loss record
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    
    -- Offensive stats
    points_scored INTEGER DEFAULT 0,
    total_yards INTEGER DEFAULT 0,
    passing_yards INTEGER DEFAULT 0,
    rushing_yards INTEGER DEFAULT 0,
    turnovers INTEGER DEFAULT 0,
    
    -- Defensive stats
    points_allowed INTEGER DEFAULT 0,
    yards_allowed INTEGER DEFAULT 0,
    takeaways INTEGER DEFAULT 0,
    
    -- Advanced metrics
    point_differential INTEGER DEFAULT 0,  -- (Points scored - points allowed)
    strength_of_schedule DECIMAL(5,3),     -- Difficulty of opponents
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure one record per team per season
    UNIQUE(team_id, season, season_type)
);

-- Overall team performance view
CREATE OR REPLACE VIEW team_performance_summary AS
SELECT 
    t.name,
    t.city,
    t.conference,
    t.division,
    COUNT(g.game_id) as games_played,
    SUM(CASE WHEN g.home_team_id = t.team_id THEN g.home_score ELSE g.away_score END) as total_points_scored,
    SUM(CASE WHEN g.home_team_id = t.team_id THEN g.away_score ELSE g.home_score END) as total_points_allowed,
    AVG(CASE WHEN g.home_team_id = t.team_id THEN g.home_score ELSE g.away_score END) as avg_points_scored,
    AVG(CASE WHEN g.home_team_id = t.team_id THEN g.away_score ELSE g.home_score END) as avg_points_allowed,
    SUM(CASE 
        WHEN g.home_team_id = t.team_id AND g.home_score > g.away_score THEN 1
        WHEN g.away_team_id = t.team_id AND g.away_score > g.home_score THEN 1
        ELSE 0 
    END) as wins,
    SUM(CASE 
        WHEN g.home_team_id = t.team_id AND g.home_score < g.away_score THEN 1
        WHEN g.away_team_id = t.team_id AND g.away_score < g.home_score THEN 1
        ELSE 0 
    END) as losses
FROM teams t
LEFT JOIN games g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
    AND g.status = 'Final'
GROUP BY t.team_id, t.name, t.city, t.conference, t.division
ORDER BY wins DESC, avg_points_scored DESC;

-- Games table indexes
CREATE INDEX IF NOT EXISTS idx_games_date ON games(date);
CREATE INDEX IF NOT EXISTS idx_games_season_week ON games(season, week);
CREATE INDEX IF NOT EXISTS idx_games_teams ON games(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);

-- Player stats indexes
CREATE INDEX IF NOT EXISTS idx_player_stats_game ON player_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_team ON player_stats(team_id);

-- Team stats indexes
CREATE INDEX IF NOT EXISTS idx_team_season_stats_lookup ON team_season_stats(team_id, season);

-- Teams table indexes
CREATE INDEX IF NOT EXISTS idx_teams_conference_division ON teams(conference, division);

-- Insert sample data
INSERT INTO teams (team_id, name, city, abbreviation, conference, division, primary_color, secondary_color, stadium_name, stadium_capacity, founded_year) VALUES
(1, 'Cowboys', 'Dallas', 'DAL', 'NFC', 'NFC East', '#003594', '#869397', 'AT&T Stadium', 80000, 1960),
(2, 'Patriots', 'New England', 'NE', 'AFC', 'AFC East', '#002244', '#C60C30', 'Gillette Stadium', 65878, 1960),
(3, 'Packers', 'Green Bay', 'GB', 'NFC', 'NFC North', '#203731', '#FFB612', 'Lambeau Field', 81441, 1919),
(4, 'Steelers', 'Pittsburgh', 'PIT', 'AFC', 'AFC North', '#FFB612', '#101820', 'Heinz Field', 68400, 1933),
(5, '49ers', 'San Francisco', 'SF', 'NFC', 'NFC West', '#AA0000', '#B3995D', 'Levi''s Stadium', 68500, 1946),
(6, 'Chiefs', 'Kansas City', 'KC', 'AFC', 'AFC West', '#E31837', '#FFB81C', 'Arrowhead Stadium', 76416, 1960),
(7, 'Bills', 'Buffalo', 'BUF', 'AFC', 'AFC East', '#00338D', '#C60C30', 'Highmark Stadium', 71608, 1960),
(8, 'Rams', 'Los Angeles', 'LAR', 'NFC', 'NFC West', '#003594', '#FFA300', 'SoFi Stadium', 70240, 1936)
ON CONFLICT (team_id) DO NOTHING; -- Don't insert if team already exists

-- Insert sample games
INSERT INTO games (game_id, season, season_type, week, date, home_team_id, away_team_id, home_score, away_score, status) VALUES
(1001, 2024, 'REG', 1, '2024-09-08', 1, 2, 21, 17, 'Final'),
(1002, 2024, 'REG', 1, '2024-09-08', 3, 4, 28, 14, 'Final'),
(1003, 2024, 'REG', 1, '2024-09-09', 5, 6, 24, 20, 'Final'),
(1004, 2024, 'REG', 2, '2024-09-15', 2, 7, 14, 31, 'Final'),
(1005, 2024, 'REG', 2, '2024-09-15', 4, 8, 17, 24, 'Final')
ON CONFLICT (game_id) DO NOTHING;

-- Create a view
CREATE OR REPLACE VIEW team_performance_summary AS
SELECT 
    t.name,
    t.city,
    t.conference,
    t.division,
    COUNT(g.game_id) as games_played,
    SUM(CASE WHEN g.home_team_id = t.team_id THEN g.home_score ELSE g.away_score END) as total_points_scored,
    SUM(CASE WHEN g.home_team_id = t.team_id THEN g.away_score ELSE g.home_score END) as total_points_allowed,
    AVG(CASE WHEN g.home_team_id = t.team_id THEN g.home_score ELSE g.away_score END) as avg_points_scored,
    AVG(CASE WHEN g.home_team_id = t.team_id THEN g.away_score ELSE g.home_score END) as avg_points_allowed,
    SUM(CASE 
        WHEN g.home_team_id = t.team_id AND g.home_score > g.away_score THEN 1
        WHEN g.away_team_id = t.team_id AND g.away_score > g.home_score THEN 1
        ELSE 0 
    END) as wins,
    SUM(CASE 
        WHEN g.home_team_id = t.team_id AND g.home_score < g.away_score THEN 1
        WHEN g.away_team_id = t.team_id A