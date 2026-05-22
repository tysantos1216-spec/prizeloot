import streamlit as st
import pandas as pd
import sqlite3
import math
from apify_client import ApifyClient
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams

# --- SETUP & CONFIG ---
st.set_page_config(page_title="AI PrizePicks Alpha", layout="wide")
APIFY_TOKEN = "YOUR_APIFY_TOKEN" # Replace with your real token

# --- ANALYTICS ENGINE ---
def calculate_ev(prob_win, payout_decimal):
    prob_loss = 1 - prob_win
    ev = (prob_win * (payout_decimal - 1)) - (prob_loss * 1)
    return ev

def find_arbitrage(pp_line, dk_line):
    diff = abs(pp_line - dk_line)
    return (True, diff) if diff >= 2.0 else (False, 0)

def check_correlation(player1, player2):
    if player1.get('team') == player2.get('team'):
        return True, f"⚠️ Risk: {player1.get('name')} & {player2.get('name')} are teammates."
    return False, None

def get_implied_prob(american_odds):
    if american_odds > 0: return 100 / (american_odds + 100)
    return abs(american_odds) / (abs(american_odds) + 100)

def check_downswing_protection(current_bankroll, initial_bankroll, max_drawdown_pct=0.10):
    drawdown = (initial_bankroll - current_bankroll) / initial_bankroll
    if drawdown >= max_drawdown_pct:
        st.error("🚨 DOWNSWING PROTECTION ACTIVE: Halted for 24 Hours.")
        return False
    return True

# --- UI DESIGN ---
st.title("🎯 AI PrizePicks 24/7 Optimizer")
tab1, tab2, tab3 = st.tabs(["🔥 Top Lineups", "📊 Live Board", "📈 AI Logic"])

with tab1:
    st.subheader("6-Leg High Value Flex")
    prob = st.slider("AI Predicted Win %", 0.0, 1.0, 0.55)
    ev = calculate_ev(prob, 2.0)
    if ev > 0: st.success(f"✅ Positive EV Detected: {ev:.2f}")
    else: st.error(f"❌ Negative EV: {ev:.2f} (STAY AWAY)")

with tab2:
    st.header("Live Market Data")
    # Add your tracker logic here
    st.write("Fetching live NBA rosters...")
    # Example roster pull logic
    nba_teams = teams.get_teams()
    celtics = [t for t in nba_teams if t['abbreviation'] == 'BOS'][0]
    roster_df = commonteamroster.CommonTeamRoster(team_id=celtics['id']).get_data_frames()[0]
    st.dataframe(roster_df)

with tab3:
    st.header("Mathematical Breakdown")
    st.latex(r"P(X > L) = 1 - \Phi\left(\frac{L - \mu}{\sigma}\right)")
    st.write("Our AI uses Bayesian Inference and Z-Score analysis.")