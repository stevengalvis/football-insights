import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import openai
import datetime

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
FOOTYSTATS_API_KEY = os.getenv("FOOTYSTATS_API_KEY")
BASE_URL = "https://api.footystats.org"
EPL_LEAGUE_ID = 1  # Premier League competition ID

# Streamlit setup
st.set_page_config(page_title="Match Insight Studio", layout="wide")
st.title("⚽ Match Insight Studio")

# Utility functions
def get_matches_by_date(date: str) -> list:
    """Fetch fixtures for a given date, then filter for EPL by competition_id."""
    url = (
        f"{BASE_URL}/fixtures-by-date"
        f"?key={FOOTYSTATS_API_KEY}&from={date}&to={date}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        # Filter to EPL fixtures only
        epl = [m for m in data if m.get("competition_id") == EPL_LEAGUE_ID]
        return epl
    except requests.exceptions.RequestException as e:
        st.error(f"FootyStats fixtures error: {e}")
        return []


def prepare_dataframe(raw: list) -> pd.DataFrame:
    """Normalize raw match list into a DataFrame and rename fields."""
    if not raw:
        return pd.DataFrame()
    df = pd.json_normalize(raw)
    # Parse dates
    df["match_date"] = pd.to_datetime(
        df.get("match_date", ""), errors='coerce'
    ).dt.date
    # Map and rename fields
    mapping = {
        "match_date": "match_date",
        "home_name": "home_name",
        "away_name": "away_name",
        "home_goal_count": "home_goals",
        "away_goal_count": "away_goals",
        "home_xg": "home_xg",
        "away_xg": "away_xg",
        "home_corners": "home_corners",
        "away_corners": "away_corners",
        "btts": "btts",
        "status": "status"
    }
    df = df.rename(columns=mapping)
    return df[list(mapping.values())]


def build_prompt(row: pd.Series, tone: str, coach: str,
                 event: str, desc: str, betting: bool) -> str:
    team_a, team_b = row.home_name, row.away_name
    score = f"{row.home_goals} - {row.away_goals}"
    context_map = {
        "FT": "post-match analysis",
        "NS": "pre-match preview",
        "1H": "in-play live summary",
        "2H": "in-play live summary",
        "HT": "halftime insight",
        "ET": "in-play live summary",
        "P": "in-play live summary"
    }
    ctx = context_map.get(row.status, "match update")
    betting_line = "Include betting insight." if betting else "Exclude betting insight."
    return (
        f"Write a {tone.lower()} tweet-style {ctx} of a football match.\n"
        f"Teams: {team_a} vs {team_b}\n"
        f"Score: {score}\n"
        f"Event: {event} - {desc}\n"
        f"Coach Notes: {coach}\n"
        f"{betting_line}\n"
        "Make it sharp, tactical, and engaging for football fans."
    )

# UI Controls
# Default to last matchday of a season the trial supports (e.g. May 19, 2024)
default_date = datetime.date(2024, 5, 19)
start_date = datetime.date(2023, 8, 1)
selected_date = st.date_input(
    "Select Match Date",
    value=default_date,
    min_value=start_date,
    max_value=default_date
)
date_str = selected_date.isoformat()

# User inputs
# ↓ Replace the "..." with the code below ↓

# 1. Fetch raw matches for the chosen date
with st.spinner("Fetching fixtures…"):
    raw_matches = get_matches_by_date(date_str)

# 2. Prepare DataFrame
df_matches = prepare_dataframe(raw_matches)

# 3. Handle no‐data / render a selectbox
if df_matches.empty:
    st.warning(f"No Premier League fixtures found on {date_str}.")
else:
    # Build a list of strings like "Arsenal vs Chelsea (2024-05-19)"
    options = df_matches.apply(
        lambda row: f"{row.home_name} vs {row.away_name} ({row.match_date})", axis=1
    ).tolist()

    selected = st.selectbox(
        "Select a match to generate insight for:", options
    )  # you can use this string later to lookup the row in df_matches

    # OPTIONAL: If you want to show the raw table as well:
    st.dataframe(df_matches, use_container_width=True)

    # Example: once they select a match, you can pull out that row:
    idx = options.index(selected)
    chosen_row = df_matches.iloc[idx]

    st.markdown(
        f"**You chose:** {chosen_row.home_name} vs {chosen_row.away_name} on {chosen_row.match_date}"
    )
    # From here, you can call `build_prompt(chosen_row, …)` or anything else.
...
