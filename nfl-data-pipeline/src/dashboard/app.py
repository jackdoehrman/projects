import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title='NFL Analytics Dashboard',
    page_icon='🏈',
    layout='wide'
)

@st.cache_data
def load_nfl_data():
    """Load NFL data - using sample data for reliability"""
    return pd.DataFrame({
        'team_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'name': ['Cowboys', 'Patriots', 'Packers', 'Steelers', '49ers', 'Chiefs', 'Bills', 'Rams'],
        'city': ['Dallas', 'New England', 'Green Bay', 'Pittsburgh', 'San Francisco', 'Kansas City', 'Buffalo', 'Los Angeles'],
        'abbreviation': ['DAL', 'NE', 'GB', 'PIT', 'SF', 'KC', 'BUF', 'LAR'],
        'conference': ['NFC', 'AFC', 'NFC', 'AFC', 'NFC', 'AFC', 'AFC', 'NFC'],
        'division': ['NFC East', 'AFC East', 'NFC North', 'AFC North', 'NFC West', 'AFC West', 'AFC East', 'NFC West']
    })

def main():
    st.title('NFL Analytics Dashboard')
    st.markdown('Interactive NFL Team Data Analysis')
    st.markdown('---')
    
    teams_df = load_nfl_data()
    
    # Sidebar filters
    st.sidebar.header('Team Filters')
    conferences = ['All'] + sorted(teams_df['conference'].unique().tolist())
    selected_conference = st.sidebar.selectbox('Conference', conferences)
    
    # Filter data
    filtered_df = teams_df.copy()
    if selected_conference != 'All':
        filtered_df = filtered_df[filtered_df['conference'] == selected_conference]
    
    # Main dashboard
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.subheader('Conference Distribution')
        conf_counts = teams_df['conference'].value_counts()
        fig = px.pie(
            values=conf_counts.values,
            names=conf_counts.index,
            title='NFL Teams by Conference',
            color_discrete_map={'AFC': '#FF4444', 'NFC': '#4444FF'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader('Division Breakdown')
        division_counts = teams_df['division'].value_counts()
        colors = ['#FF4444' if 'AFC' in div else '#4444FF' for div in division_counts.index]
        fig = go.Figure(data=[go.Bar(
            x=division_counts.index,
            y=division_counts.values,
            marker_color=colors
        )])
        fig.update_layout(title='Teams per Division', xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader('Quick Stats')
        st.metric('Total Teams', len(teams_df))
        st.metric('AFC Teams', len(teams_df[teams_df['conference'] == 'AFC']))
        st.metric('NFC Teams', len(teams_df[teams_df['conference'] == 'NFC']))
    
    # Team listing
    st.subheader(f'Team Directory ({len(filtered_df)} teams)')
    if not filtered_df.empty:
        display_df = filtered_df[['name', 'city', 'abbreviation', 'conference', 'division']].copy()
        display_df.columns = ['Team', 'City', 'Abbrev', 'Conference', 'Division']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

if __name__ == '__main__':
    main()