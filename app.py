import streamlit as st
import pandas as pd
import random
import os

# --- CONFIGURATION ---
PLAYERS_LIST = ["John", "Kalida", "Meredith", "Eric", "Grant"]
COUNTRIES = [
    "Albania", "Andorra", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", 
    "Belgium", "Benin", "Bolivia", "Bosnia and Herzegovina", "Brazil", "Bulgaria", 
    "Canada", "Chile", "China", "Chinese Taipei", "Colombia", "Croatia", "Cyprus", 
    "Czech Republic", "Denmark", "Ecuador", "Eritrea", "Estonia", "Finland", "France", 
    "Georgia", "Germany", "Ghana", "Great Britain", "Greece", "Guinea-Bissau", "Haiti", 
    "Hong Kong", "Hungary", "Iceland", "India", "Individual Neutral Athletes", "Iran", 
    "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Kazakhstan", "Kenya", "Kosovo", 
    "Kyrgyzstan", "Latvia", "Lebanon", "Liechtenstein", "Lithuania", "Luxembourg", 
    "Madagascar", "Malaysia", "Malta", "Mexico", "Moldova", "Monaco", "Mongolia", 
    "Montenegro", "Morocco", "Netherlands", "New Zealand", "Nigeria", "North Macedonia", 
    "Norway", "Pakistan", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", 
    "Romania", "San Marino", "Saudi Arabia", "Serbia", "Slovakia", "Slovenia", 
    "South Africa", "South Korea", "Spain", "Sweden", "Switzerland", "Thailand", 
    "Trinidad and Tobago", "Turkey", "Ukraine", "United Arab Emirates", "United States", 
    "Uruguay", "Uzbekistan"
]
ROUNDS = 3
CSV_FILE = "./data/country_roster.csv"

st.set_page_config(page_title="2026 Olympic Draft", layout="wide")
st.title("🏆 2026 Milano Cortina Draft")

# --- SESSION STATE INITIALIZATION ---
if 'drafted_data' not in st.session_state:
    st.session_state.drafted_data = pd.read_csv(CSV_FILE).to_dict('records') if os.path.exists(CSV_FILE) else []

if 'player_order' not in st.session_state:
    st.session_state.player_order = None # Order stays empty until button is clicked

# --- SIDEBAR: DRAFT ORDER ---
with st.sidebar:
    st.header("⚙️ Draft Setup")
    if st.button("🎲 Randomize Draft Order"):
        order = PLAYERS_LIST.copy()
        random.shuffle(order)
        st.session_state.player_order = order
        st.rerun()

    if st.session_state.player_order:
        st.subheader("The Order:")
        for i, player in enumerate(st.session_state.player_order):
            st.write(f"{i+1}. **{player}**")
    else:
        st.warning("Order not set. Click the button to start!")

# --- DRAFT LOGIC ---
if st.session_state.player_order:
    players = st.session_state.player_order # Use the randomized order
    total_picks = len(players) * ROUNDS
    current_pick_num = len(st.session_state.drafted_data)

    if current_pick_num < total_picks:
        round_idx = (current_pick_num // len(players)) + 1
        player_idx = current_pick_num % len(players)
        
        # Snake Logic
        current_round_players = players if round_idx % 2 != 0 else list(reversed(players))
        current_picker = current_round_players[player_idx]

        st.header(f"Round {round_idx}: {current_picker}'s Turn (Pick #{current_pick_num + 1})")

        drafted_names = [d['country'] for d in st.session_state.drafted_data]
        search_query = st.text_input("🔍 Search for a country:", "").lower()
        available = [c for c in COUNTRIES if c not in drafted_names and search_query in c.lower()]

        cols = st.columns(4)
        for i, country in enumerate(available):
            if cols[i % 4].button(f"Draft {country}", use_container_width=True):
                new_pick = {"country": country, "owner": current_picker, 
                            "draft_pick": current_pick_num + 1, "draft_round": round_idx}
                st.session_state.drafted_data.append(new_pick)
                pd.DataFrame(st.session_state.drafted_data).to_csv(CSV_FILE, index=False)
                st.rerun()
    else:
        st.balloons()
        st.success("Draft Complete!")

# --- RESULTS ---
st.divider()
if st.session_state.drafted_data:
    st.subheader("Draft Summary")
    st.table(pd.DataFrame(st.session_state.drafted_data))

if st.sidebar.button("⚠️ Reset Everything"):
    if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
    st.session_state.clear()
    st.rerun()