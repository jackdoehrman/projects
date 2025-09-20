-- Team Chemistry Rankings
SELECT 
    team_name,
    team_abbreviation,
    wins || '-' || losses as record,
    ROUND(W_PCT, 3) as win_percentage,
    chemistry_rating,
    ROUND(net_rating, 1) as net_rating,
    plus_minus
FROM team_performance 
ORDER BY CHEMISTRY_SCORE DESC;

-- Offensive vs Defensive Efficiency
SELECT 
    team_name,
    ROUND(offensive_rating, 1) as off_rating,
    ROUND(defensive_rating, 1) as def_rating,
    ROUND(net_rating, 1) as net_rating,
    CASE 
        WHEN net_rating > 5 THEN 'Elite'
        WHEN net_rating > 0 THEN 'Above Average'
        WHEN net_rating > -5 THEN 'Below Average'
        ELSE 'Poor'
    END as efficiency_tier
FROM team_performance 
ORDER BY net_rating DESC;

-- Shooting Analysis
SELECT 
    team_name,
    ROUND(FG_PCT, 3) as field_goal_pct,
    ROUND(FG3_PCT, 3) as three_point_pct,
    ROUND(FT_PCT, 3) as free_throw_pct,
    ROUND((FG_PCT + FG3_PCT + FT_PCT) / 3, 3) as overall_shooting
FROM team_performance 
ORDER BY overall_shooting DESC;

-- Ball Movement Analysis
SELECT 
    team_name,
    AST as assists,
    TOV as turnovers,
    ROUND(CAST(AST AS FLOAT) / TOV, 2) as assist_turnover_ratio,
    CASE 
        WHEN CAST(AST AS FLOAT) / TOV >= 2.0 THEN 'Excellent'
        WHEN CAST(AST AS FLOAT) / TOV >= 1.5 THEN 'Good'
        WHEN CAST(AST AS FLOAT) / TOV >= 1.0 THEN 'Average'
        ELSE 'Poor'
    END as ball_movement_grade
FROM team_performance 
ORDER BY assist_turnover_ratio DESC;