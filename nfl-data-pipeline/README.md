# NFL Data Engineering Pipeline

Production-ready data engineering solution for NFL analytics with Docker, PostgreSQL, ETL automation, and interactive dashboards.

## Architecture
- **Extract**: SportsData.io API integration
- **Transform**: pandas data processing and feature engineering  
- **Load**: PostgreSQL data warehouse with normalized schema
- **Visualize**: Streamlit dashboard with interactive charts

## Tech Stack
- **Infrastructure**: Docker, Docker Compose, PostgreSQL
- **Backend**: Python, pandas, SQLAlchemy
- **Frontend**: Streamlit, Plotly
- **APIs**: SportsData.io NFL API

## Quick Start
```bash
# Get API key from https://sportsdata.io/
cp .env.example .env
# Add your API key to .env

docker-compose up -d
# Access dashboard: http://localhost:8501