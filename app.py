import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI


# Load OpenAI API key from .env
load_dotenv()
client = OpenAI()
# Pass the key explicitly from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit app layout
st.set_page_config(page_title="Match Insight Studio", layout="wide")
st.title("⚽ Match Insight Studio")

# Match input section
st.header("Match Info")
team_a = st.text_input("Team A", placeholder="e.g. Barcelona")
team_b = st.text_input("Team B", placeholder="e.g. Real Madrid")
score = st.text_input("Current Score", placeholder="e.g. 1-0")
minute = st.slider("Minute", 0, 120, 45)
event_type = st.selectbox("Key Event", ["None", "Goal", "Red Card", "Injury", "Penalty", "Tactical Shift"])
event_desc = st.text_area("Event Description")

# Optional context
st.header("Optional Context")
coach_notes = st.text_area("Coach Notes", placeholder="e.g. Coach X tends to bunker after scoring.")
include_betting = st.checkbox("Include betting insights?")
tone = st.selectbox("Tone", ["Neutral", "Tactical", "Casual", "Spicy Twitter", "Insightful Analyst"])

# Submit button
if st.button("Generate Summary"):
    with st.spinner("Generating summary..."):
        try:
            prompt = f"""
            Write a {tone.lower()} tweet-style summary of a football match.
            Teams: {team_a} vs {team_b}
            Score: {score}, Minute: {minute}
            Event: {event_type} - {event_desc}
            Coach Notes: {coach_notes}
            {"Include betting insight in the summary." if include_betting else "Exclude betting insight."}
            Make it sharp, tactical, and engaging for football fans.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=180
            )

            summary = response.choices[0].message.content
            st.success("Summary Generated")
            st.text_area("Generated Summary", value=summary, height=200)

        except Exception as e:
            st.error(f"Error: {e}")


