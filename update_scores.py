import pandas as pd
import os
import json
from dotenv import load_dotenv

# kaggle imports creds on import so load_dotenv first
load_dotenv()
from kaggle.api.kaggle_api_extended import KaggleApi 

def set_base_scores(df, points_per_disc = 120, max_base_score = 15):
    """
    Calculates the base_score for each event.
    Logic: MIN(total_pool / number_of_events_in_discipline, max_cap)
    """
    # 1. Count events per discipline and map it back to every row
    df['events_in_discipline'] = df.groupby('discipline')['discipline'].transform('count')
    
    # 2. Perform the math: 120 / N
    df['base_score'] = points_per_disc / df['events_in_discipline']
    
    # 3. Apply the cap (e.g., no event is worth more than 15)
    df['base_score'] = df['base_score'].clip(upper=max_base_score).round(2)
    
    # Clean up the helper column
    return df.drop(columns=['events_in_discipline'])   

def calculate_leaderboard():
    # 1. Authenticate with Kaggle (using Secrets in Github)
    api = KaggleApi()
    api.authenticate()
    
    # 2. Download latest medal data
    #api.dataset_download_files('piterfm/milano-cortina-2026-olympic-winter-games', path='./data', unzip=True)
    
    # 3. Load your sources of truth
    events_df = pd.read_csv('./data/milano_2026_events.csv')
    roster_df = pd.read_csv('./data/country_roster.csv')
    medals_df = pd.read_csv('./data/medals.csv') # Assuming standard Kaggle naming

    set_base_scores(events_df)

    # 4. The Math: Join Medals -> Events -> Roster
    results = medals_df.merge(events_df, on='event')
    results = results.merge(roster_df, on='country')

    #calculate base score

    def calc_points(row):
        multiplier = 5.0 if row['medal'] == 'Gold' else 3.0 if row['medal'] == 'Silver' else 2.0
        prestige = 3 if row['is_prestige'] else 1
        return row['base_score'] * multiplier * prestige

    results['points_earned'] = results.apply(calc_points, axis=1)

    print(results[['country', 'event', 'medal', 'owner', 'base_score', 'points_earned']].head(5))
    
    # 5. Group by Owner for the leaderboard
    leaderboard = results.groupby('owner')['points_earned'].sum().sort_values(ascending=False).to_dict()
    
    # 6. Save as JSON for your website to read
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

if __name__ == "__main__":
    calculate_leaderboard()