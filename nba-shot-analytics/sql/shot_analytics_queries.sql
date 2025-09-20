-- Player shooting efficiency by zone
SELECT 
    player_name,
    team_name,
    total_attempts,
    ROUND(overall_fg_pct, 3) as overall_fg_pct,
    ROUND(at_rim_fg_pct, 3) as at_rim_fg_pct,
    ROUND(three_point_pct, 3) as three_point_pct,
    ROUND(midrange_fg_pct, 3) as midrange_fg_pct,
    ROUND(shot_selection_score, 1) as selection_score
FROM player_shooting 
ORDER BY shot_selection_score DESC;

-- Team efficiency rankings
SELECT 
    team_name,
    team_abbreviation,
    ROUND(close_range_pct, 3) as close_range_pct,
    ROUND(three_point_pct, 3) as three_point_pct,
    ROUND(overall_efficiency_score, 1) as efficiency_score
FROM team_efficiency 
ORDER BY overall_efficiency_score DESC;

-- Shot type distribution analysis
SELECT 
    player_name,
    at_rim_attempts,
    three_point_attempts,
    midrange_attempts,
    total_attempts,
    ROUND(CAST(at_rim_attempts AS FLOAT) / total_attempts * 100, 1) as at_rim_pct,
    ROUND(CAST(three_point_attempts AS FLOAT) / total_attempts * 100, 1) as three_point_pct,
    ROUND(CAST(midrange_attempts AS FLOAT) / total_attempts * 100, 1) as midrange_pct
FROM player_shooting 
WHERE total_attempts > 0
ORDER BY shot_selection_score DESC;

-- High volume vs efficiency analysis
SELECT 
    player_name,
    total_attempts,
    ROUND(overall_fg_pct, 3) as fg_pct,
    ROUND(shot_selection_score, 1) as selection_score,
    CASE 
        WHEN total_attempts >= 100 AND overall_fg_pct >= 0.500 THEN 'High Volume + High Efficiency'
        WHEN total_attempts >= 100 THEN 'High Volume'
        WHEN overall_fg_pct >= 0.500 THEN 'High Efficiency'
        ELSE 'Developing'
    END as player_category
FROM player_shooting 
ORDER BY total_attempts DESC, overall_fg_pct DESC;