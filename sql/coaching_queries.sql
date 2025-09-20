-- Team Performance Summary
SELECT 
    team,
    COUNT(*) as games_played,
    ROUND(AVG(total_epa), 2) as avg_epa,
    ROUND(AVG(success_rate), 2) as avg_success_rate,
    ROUND(AVG(red_zone_td_rate), 2) as red_zone_efficiency
FROM team_performance 
WHERE team IS NOT NULL
GROUP BY team 
ORDER BY avg_epa DESC;

-- Weekly Performance Trends
SELECT 
    team,
    week,
    total_epa,
    success_rate,
    LAG(total_epa) OVER (PARTITION BY team ORDER BY week) as prev_week_epa
FROM team_performance 
WHERE team IS NOT NULL
ORDER BY team, week;

-- Top Performers
SELECT 'EPA Leaders' as metric, team, ROUND(AVG(total_epa), 2) as value
FROM team_performance 
WHERE team IS NOT NULL
GROUP BY team 
ORDER BY value DESC 
LIMIT 5;