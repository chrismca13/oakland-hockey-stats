import streamlit as st
import pandas as pd
import logging
import os

# Load data from S3
@st.cache_data()
def load_data():

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            "s3://gang-green-hockey/ALL_OaklandHockeyData_CURRENT.csv"
        )
        logging.info(f"Loaded CSV from S3, shape={df.shape}")
    except Exception as e:
        logging.exception("Failed to load data from S3")
        st.error(f"Failed to load data from S3: {e}")

    return df

df = load_data()

st.title("Oakland Beer League Hockey Stats")

# Sidebar filters
teams = sorted(df['Team'].dropna().unique())
players = sorted(df['Name'].dropna().unique())


selected_teams = st.sidebar.multiselect("Filter by Team(s)", teams, default=teams)
selected_player = st.sidebar.text_input("Search Player Name")

filtered_df = df.copy()
if selected_teams:
    filtered_df = filtered_df[filtered_df['Team'].isin(selected_teams)]

# Slider filters for stats
gp_min, gp_max = int(df['GP'].min()), int(df['GP'].max())
goals_min, goals_max = int(df['Goals'].min()), int(df['Goals'].max())
ass_min, ass_max = int(df['Ass.'].min()), int(df['Ass.'].max())
pts_min, pts_max = int((df['Goals'] + df['Ass.']).min()), int((df['Goals'] + df['Ass.']).max())
if 'Min' in df.columns:
    min_min, min_max = int(df['Min'].min()), int(df['Min'].max())

gp_slider = st.sidebar.slider('Games Played (GP)', gp_min, gp_max, (gp_min, gp_max))
goals_slider = st.sidebar.slider('Goals', goals_min, goals_max, (goals_min, goals_max))
ass_slider = st.sidebar.slider('Assists', ass_min, ass_max, (ass_min, ass_max))
pts_slider = st.sidebar.slider('Points', pts_min, pts_max, (pts_min, pts_max))
if 'Min' in df.columns:
    min_slider = st.sidebar.slider('Minutes (Min)', min_min, min_max, (min_min, min_max))

# Apply slider filters
filtered_df = filtered_df[
    (filtered_df['GP'] >= gp_slider[0]) & (filtered_df['GP'] <= gp_slider[1]) &
    (filtered_df['Goals'] >= goals_slider[0]) & (filtered_df['Goals'] <= goals_slider[1]) &
    (filtered_df['Ass.'] >= ass_slider[0]) & (filtered_df['Ass.'] <= ass_slider[1]) &
    ((filtered_df['Goals'] + filtered_df['Ass.']) >= pts_slider[0]) & ((filtered_df['Goals'] + filtered_df['Ass.']) <= pts_slider[1])
]
if 'Min' in df.columns:
    filtered_df = filtered_df[(filtered_df['Min'] >= min_slider[0]) & (filtered_df['Min'] <= min_slider[1])]

# Add player name filter
if selected_player and selected_player.strip():
    filtered_df = filtered_df[filtered_df['Name'].str.contains(selected_player.strip(), case=False, na=False)]

# Sortable table
st.subheader("Player Stats Table")
st.dataframe(filtered_df.sort_values(by=['Goals', 'Ass.', 'Pts'], ascending=False).reset_index(drop=True), width='stretch')


# Apply filters to the bar chart as well, and sort x-axis by Points
filtered_top_scorers = (
    filtered_df.groupby('Name', as_index=False)
    .agg({'Goals': 'sum', 'Ass.': 'sum'})
    .assign(Points=lambda x: x['Goals'] + x['Ass.'])
)
# Sort by Points and select top 10
filtered_top_scorers = filtered_top_scorers.sort_values('Points', ascending=False).head(10)

import plotly.express as px
st.subheader("Games Played vs Points (Scatter Plot)")
scatter_df = (
    filtered_df.groupby('Name', as_index=False)
    .agg({'GP': 'sum', 'Goals': 'sum', 'Ass.': 'sum'})
    .assign(Pts=lambda x: x['Goals'] + x['Ass.'])
)

scatter_df['GP'] = pd.to_numeric(scatter_df['GP'], errors='coerce')
scatter_df['Pts'] = pd.to_numeric(scatter_df['Pts'], errors='coerce')

# Highlight searched player if provided
scatter_df['Highlighted'] = 'Other Players'
if selected_player and selected_player.strip():
    scatter_df.loc[scatter_df['Name'].str.contains(selected_player.strip(), case=False, na=False), 'Highlighted'] = 'Searched Player'

fig = px.scatter(
    scatter_df,
    x='GP',
    y='Pts',
    hover_name='Name',
    hover_data=['Goals', 'Ass.', 'Pts'],
    color='Highlighted',
    color_discrete_map={'Searched Player': '#FF6B6B', 'Other Players': '#4C72B0'},
    title='Games Played vs Points'
)
st.plotly_chart(fig, use_container_width=True)