# NBA Shot Selection & Efficiency Analytics

## Overview
Advanced NBA shot analytics platform analyzing shooting efficiency, shot selection quality, and spatial shooting patterns for player evaluation and strategic planning.

## Features
- **Interactive Shot Charts**: Visual shot location and efficiency mapping
- **Zone Efficiency Analysis**: Performance breakdown by court areas
- **Shot Selection Scoring**: Custom metric evaluating shot quality
- **Team Efficiency Comparison**: Multi-dimensional team shooting analysis
- **Distance Analysis**: Shooting performance by shot distance ranges
- **Heat Map Visualizations**: Spatial shooting pattern analysis

## Technical Skills Demonstrated
✅ NBA API Integration & Spatial Data Processing  
✅ Advanced Basketball Shot Analytics  
✅ Interactive Data Visualization & Heat Maps  
✅ Custom Metric Development (Shot Selection Score)  
✅ Spatial Analysis & Court Mapping  
✅ Multi-dimensional Efficiency Analysis  

## Key Metrics
- **Shot Selection Score**: Weighted efficiency metric favoring high-value shots
- **Zone Efficiency**: FG% breakdown by court areas (At Rim, Paint, Mid-Range, 3PT)
- **Expected vs Actual**: Shot quality analysis based on distance and location
- **Team Efficiency Score**: Comprehensive team shooting effectiveness metric

## Setup & Usage
```bash
pip install nba-api pandas plotly dash matplotlib seaborn numpy
py src/data_extraction.py
py src/data_processing.py
py src/dashboard.py  # http://127.0.0.1:8050/
py src/analysis.py
