import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

# Page config
st.set_page_config(page_title="Win Probability Visualizer", layout="wide")

# Title
st.title("IPL Win Probability")

# Load data

with open("wp_pred_output.pkl", "rb") as file:
        df_final = pickle.load(file)

# Match ID input
match_id = st.number_input("Enter Match ID", min_value=0, step=1)
st.info("Open the specific match on ESPNcricinfo and copy the long number at the end of the URL.")

# Filter the data
match_df = df_final[df_final['p_match'] == match_id].copy()

# Check if match data is available
if match_df.empty:
    st.warning("No data available for the selected match.")
else:
    # Adjust innings 2 x-axis
    end_innings_1 = match_df[match_df['inns'] == 1]['inns_balls'].max()
    match_df.loc[match_df['inns'] == 2, 'inns_balls'] += end_innings_1

    # Detect wickets (where inns_wkts increases)
    match_df['prev_wkts'] = match_df.groupby('inns')['inns_wkts'].shift(1)
    wicket_df = match_df[match_df['inns_wkts'] > match_df['prev_wkts']]

    # Prepare for line plot
    x = match_df['inns_balls'].values
    y = match_df['win_prob'].values

    # Create line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Color segments based on win probability
    colors = ['steelblue' if prob > 50 else 'darkorange' for prob in y[:-1]]
    cmap = {'steelblue': (0, 0.45, 0.8, 1), 'darkorange': (1, 0.55, 0, 1)}
    line_colors = [cmap[c] for c in colors]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    lc = LineCollection(segments, colors=line_colors, linewidths=2)
    ax.add_collection(lc)

    # Wicket circle markers (filled red)
    ax.plot(wicket_df['inns_balls'], wicket_df['win_prob'],
            'o', markerfacecolor='red', markeredgecolor='red',
            linestyle='None', markersize=6, markeredgewidth=1, alpha=0.8)

    # Set plot limits
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(0, 110)

    # Reference lines
    ax.axhline(y=50, color='black', linestyle='--', alpha=0.3)
    ax.axvline(x=end_innings_1, color='black', linestyle='--', alpha=0.3)

    # Y-axis team labels
    team1 = match_df[match_df['inns'] == 1]['team_bat'].iloc[0]
    team2 = match_df[match_df['inns'] == 2]['team_bat'].iloc[0]
    ax.text(x.min() - 2, 75, team1, rotation=90, fontsize=8, va='center')
    ax.text(x.min() - 2, 25, team2, rotation=90, fontsize=8, va='center')

    # Y-axis ticks
    ax.set_yticks([0, 50, 100])
    ax.set_yticklabels(['100%', '50%', '100%'], fontsize=8)

    # X-axis: no ticks, but add innings labels
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    mid_inns1 = match_df[match_df['inns'] == 1]['inns_balls'].mean()
    mid_inns2 = match_df[match_df['inns'] == 2]['inns_balls'].mean()
    ax.text(mid_inns1, -10, 'Innings 1', ha='center', fontsize=9)
    ax.text(mid_inns2, -10, 'Innings 2', ha='center', fontsize=9)

    # Display
    st.pyplot(fig)

# Sidebar footer
st.sidebar.write("Built by [Vijay](https://www.linkedin.com/in/vijay-sundaram/)", unsafe_allow_html=True)

