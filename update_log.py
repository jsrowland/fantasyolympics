import pandas as pd
import os
import json
from dotenv import load_dotenv

# kaggle imports creds on import so load_dotenv first
load_dotenv()
from kaggle.api.kaggle_api_extended import KaggleApi

DATA_DIR = './mock_data'

def update_log():
    """
    Updates the daily player score json.    
    Will overwrite every day's score as necessary.
    """
    events_df = pd.read_csv(DATA_DIR + '/events.csv')    
    roster_df = pd.read_csv(DATA_DIR + '/roster.csv')
    medals_df = pd.read_csv(DATA_DIR + '/medals.csv')

    results = medals_df.merge(events_df, on='event')
    results = results.merge(roster_df, on='country')

    # Append calculated medal_points to each row
    medal_map = {"Gold Medal": 5.0, "Silver Medal": 3.0, "Bronze Medal": 2.0}
    results['medal_points'] = results['medal_type'].map(medal_map) * results['base_score']

    # Pre-calculate total athletes per owner (Step 4.2/4.3 helper)
    owner_total_athletes = roster_df.groupby('owner')['athletes'].sum().to_dict()

    # 3. Get a sorted list of medal_dates
    results['medal_date'] = pd.to_datetime(results['medal_date'])
    unique_dates = sorted(results['medal_date'].unique())

    score_log = []

    # 4. Calculate scores for each date snapshot
    for current_date in unique_dates:
        # Filter data up to the current loop date (running total)
        current_results = results[results['medal_date'] <= current_date]
        
        player_stats = {}
        
        # Calculate per-player stats
        for player in roster_df['owner'].unique():
            # 4.1. Medal Score: Sum of all points earned by player's countries
            player_medals = current_results[current_results['owner'] == player]
            medal_score = player_medals['medal_points'].sum()
            
            # Get total delegate size for the player's drafted countries
            total_delegate = owner_total_athletes.get(player, 1) # Avoid div by zero

            # 4.2. PA Score: medal_score / total athletes
            pa_score = medal_score / total_delegate

            player_stats[player] = {
                "medal_score": round(medal_score, 2),
                "pa_score": round(pa_score, 4),
            }

        # Calculate normalized stats
        df_snapshot = pd.DataFrame.from_dict(player_stats, orient='index')
        df_snapshot['norm_medal'] = (df_snapshot['medal_score'] / df_snapshot['medal_score'].sum()).round(4)
        df_snapshot['norm_pa']    = (df_snapshot['pa_score'] / df_snapshot['pa_score'].sum()).round(4)
        df_snapshot['daily_score'] = (20 * df_snapshot['norm_medal'] + 80 * df_snapshot['norm_pa']).round(2)

        # Add the date entry to the log
        score_log.append({
            "timestamp": current_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "players": df_snapshot.to_dict(orient='index')
        })

    # Save to the score_log.json
    with open('score_log.json', 'w') as f:
        json.dump(score_log, f, indent=2)
    
    print(f"✅ score_log.json updated with {len(unique_dates)} dates.")

if __name__ == "__main__": 
    update_log()