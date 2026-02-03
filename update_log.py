import pandas as pd
import argparse
import json
from dotenv import load_dotenv

def pull_data():
    # kaggle imports creds on import so load_dotenv first
    load_dotenv()
    from kaggle import api

    api.authenticate()

    #dataset_slug = "piterfm/milano-cortina-2026-olympic-winter-games"
    dataset_slug = "piterfm/paris-2024-olympic-summer-games" # testing
    api.dataset_download_files(dataset_slug, path='./data', unzip=True)

    results_df = pd.read_csv('./data/results.csv')
    schedules_df = pd.read_csv('./data/schedules.csv')

def update_log(data_dir):
    """
    Updates the daily player score json.    
    Will overwrite every day's score as necessary.
    """
    events_df = pd.read_csv(data_dir + '/events.csv')    
    roster_df = pd.read_csv(data_dir + '/roster.csv')
    medals_df = pd.read_csv(data_dir + '/medals.csv')

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

    # Create the "News Feed" entries
    news_feed = []
    # Sort results by date descending so newest news is first
    for _, row in results.sort_values(by='medal_date', ascending=False).iterrows():
        news_feed.append({
            "date": row['medal_date'].strftime("%b %d, %Y"),
            "entry": f"**{row['name']}** ({row['country']}, {row['athletes']} athletes) takes {row['medal_type']} in {row['event']}, winning **{row['owner']}** {row['medal_points']:.2f} points!"
        })

    # Create the "Medal Table" entries (Country-level breakdown)
    medal_breakdown = results.groupby('country').agg(
        golds=('medal_type', lambda x: (x == 'Gold Medal').sum()),
        silvers=('medal_type', lambda x: (x == 'Silver Medal').sum()),
        bronzes=('medal_type', lambda x: (x == 'Bronze Medal').sum()),
        medal_points=('medal_points', 'sum'),
        athletes=('athletes', 'first'),
        owner=('owner', 'first')
    )
    medal_breakdown['pa_score'] = medal_breakdown['medal_points'] / medal_breakdown['athletes']
    
    # Merge with roster_df (and handle potential duplicate columns) to capture countries w/o medals
    final_table = roster_df.merge(
        medal_breakdown.reset_index(), 
        on='country', 
        how='left',
        suffixes=('', '_drop') # Use suffixes=(None, '_drop') so original columns stay as-is
    ).fillna(0)

    # Drop any duplicate columns that popped up during merge
    final_table = final_table.drop(columns=[c for c in final_table.columns if '_drop' in c])

    medal_table_data = final_table.to_dict(orient='records')

    # Combine everything into one master file
    dashboard_data = {
        "history": score_log, # Your existing time-series data
        "medal_table": medal_table_data,
        "news": news_feed
    }

    with open('dashboard_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✅ score_log.json updated with {len(unique_dates)} dates.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Milano 2026 Score Updater")
    # 'store_true' means if the flag is present, debug = True. Otherwise, False.
    parser.add_argument('--debug', action='store_true', help="Use mock data and skip live pull")
    
    args = parser.parse_args()

    # 4. Implement your conditional logic
    if args.debug:
        print("🛠️ DEBUG MODE: Skipping pull, using ./mock_data")
        update_log('./mock_data')
    else:
        print("🚀 PRODUCTION MODE: Pulling live data...")
        pull_data()
        update_log('./data')