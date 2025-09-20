-- Top developing players by age group
SELECT 
    CASE 
        WHEN age <= 22 THEN 'Young (≤22)'
        WHEN age <= 25 THEN 'Prime Development (23-25)'
        ELSE 'Veteran (26+)'
    END as age_group,
    PLAYER_NAME,
    age,
    points_per_game,
    ts_percentage,
    development_score
FROM player_development 
WHERE season = '2023-24'
ORDER BY age_group, development_score DESC;

-- Players with biggest improvements
SELECT 
    PLAYER_NAME,
    team,
    age,
    ROUND(OVERALL_IMPROVEMENT, 2) as improvement_score,
    ROUND(points_per_game, 1) as current_ppg,
    ROUND(ts_percentage, 3) as current_ts_pct
FROM player_development 
WHERE OVERALL_IMPROVEMENT IS NOT NULL
ORDER BY OVERALL_IMPROVEMENT DESC
LIMIT 15;

-- Breakout candidate analysis
SELECT 
    PLAYER_NAME,
    TEAM_ABBREVIATION as team,
    AGE,
    ROUND(PTS, 1) as ppg,
    ROUND(TS_PCT, 3) as ts_pct,
    ROUND(USG_RATE, 1) as usage_rate,
    ROUND(BREAKOUT_PROB, 3) as breakout_probability
FROM breakout_candidates 
ORDER BY BREAKOUT_PROB DESC;

-- Team development summary
SELECT 
    team,
    COUNT(*) as young_players,
    ROUND(AVG(development_score), 2) as avg_dev_score,
    ROUND(AVG(ts_percentage), 3) as avg_efficiency
FROM player_development 
WHERE age <= 25 AND season = '2023-24'
GROUP BY team 
ORDER BY avg_dev_score DESC;