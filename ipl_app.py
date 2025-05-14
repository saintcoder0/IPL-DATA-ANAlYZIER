import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏏 IPL Cricket Data Analysis Dashboard")

# Load data
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries.csv")

# Sidebar filters
season = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))

# Filter data
season_matches = matches[matches['season'] == season]

st.subheader(f"📅 Matches Played in {season}")
st.write(f"Total Matches: {len(season_matches)}")

# Plot: Team wins that season
wins = season_matches['winner'].value_counts()
fig, ax = plt.subplots()
wins.plot(kind='bar', ax=ax, color='skyblue')
ax.set_ylabel("Wins")
ax.set_title("Team Wins in Selected Season")
st.pyplot(fig)

# Toss vs Match win analysis
st.subheader("🎯 Toss Advantage Analysis")
toss_match = season_matches[season_matches['toss_winner'] == season_matches['winner']]
percentage = len(toss_match) / len(season_matches) * 100
st.metric(label="Toss Winner Match Win %", value=f"{percentage:.2f}%")

# Top Batsmen
st.subheader("🏏 Top 10 Run Scorers")
top_batsmen = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_batsmen)

# Merge season info into deliveries
deliveries = deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id')

# Function to get top batsman for a season
def get_top_batsman(season_selected):
    season_data = deliveries[deliveries['season'] == season_selected]
    top_batsman = (
        season_data.groupby('batter')['batsman_runs']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(1)
    )
    return top_batsman

# In the Streamlit UI
st.subheader("🏅 Best Batsman of the Season")

top_batsman = get_top_batsman(season)

if not top_batsman.empty:
    player = top_batsman.iloc[0]['batter']
    runs = top_batsman.iloc[0]['batsman_runs']
    st.success(f"🏆 In {season}, the best batsman was **{player}** with **{int(runs)}** runs.")
else:
    st.warning("No data available for this season.")

def get_top5_batsmen(season_selected):
    season_data = deliveries[deliveries['season'] == season_selected]
    top5 = (
        season_data.groupby('batter')['batsman_runs']
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    return top5

st.subheader("🏏 Top 5 Batsmen This Season")
top5 = get_top5_batsmen(season)
st.bar_chart(top5)

def get_top_bowler(season_selected):
    season_data = deliveries[deliveries['season'] == season_selected]

    # Exclude non-bowler dismissals like run outs
    valid_dismissals = season_data[season_data['dismissal_kind'].notnull()]
    valid_dismissals = valid_dismissals[~valid_dismissals['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])]

    # Count dismissals per bowler
    top_bowler = (
        valid_dismissals.groupby('bowler')['player_dismissed']
        .count()
        .sort_values(ascending=False)
        .reset_index()
        .head(1)
    )
    return top_bowler

st.subheader("🎯 Best Bowler (Purple Cap) of the Season")

top_bowler = get_top_bowler(season)

if not top_bowler.empty:
    bowler_name = top_bowler.iloc[0]['bowler']
    wickets = top_bowler.iloc[0]['player_dismissed']
    st.success(f"🏅 In {season}, the best bowler was **{bowler_name}** with **{int(wickets)}** wickets.")
else:
    st.warning("No bowling data available for this season.")

def get_top5_bowlers(season_selected):
    season_data = deliveries[deliveries['season'] == season_selected]
    valid_dismissals = season_data[season_data['dismissal_kind'].notnull()]
    valid_dismissals = valid_dismissals[~valid_dismissals['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])]

    top5 = (
        valid_dismissals.groupby('bowler')['player_dismissed']
        .count()
        .sort_values(ascending=False)
        .head(5)
    )
    return top5

st.subheader("🎯 Top 5 Bowlers This Season")
top5_bowlers = get_top5_bowlers(season)
st.bar_chart(top5_bowlers)

def get_batsmen_with_strike_rate(season_selected, min_strike_rate=130):
    season_data = deliveries[deliveries['season'] == season_selected]

    batsman_stats = (
        season_data.groupby('batter')
        .agg({
            'batsman_runs': 'sum',
            'ball': 'count'
        })
        .rename(columns={'ball': 'balls_faced'})
    )

    batsman_stats = batsman_stats[batsman_stats['balls_faced'] >= 10]  # Ignore players with too few balls
    batsman_stats['strike_rate'] = (batsman_stats['batsman_runs'] / batsman_stats['balls_faced']) * 100

    return batsman_stats[batsman_stats['strike_rate'] >= min_strike_rate].sort_values(by='strike_rate', ascending=False)

st.subheader("⚡ High Strike Rate Batsmen This Season")

# Strike rate threshold selector
min_sr = st.slider("Minimum Strike Rate", min_value=100, max_value=200, value=130, step=5)

# Call the function
high_sr_batsmen = get_batsmen_with_strike_rate(season, min_sr)

# Show top 10 high strike rate batsmen
if not high_sr_batsmen.empty:
    st.write(high_sr_batsmen[['batsman_runs', 'balls_faced', 'strike_rate']].head(10))
else:
    st.warning("No batsmen found with strike rate above selected threshold.")


