import pandas as pd
import argparse
import json
import os
from dotenv import load_dotenv

MAPPING_FILE = 'event_mapping.json'
EXCEPTIONS_FILE = 'missing_events.json'

def pull_data():
    # kaggle imports creds on import so load_dotenv first
    load_dotenv()
    from kaggle import api

    api.authenticate()

    dataset_slug = "piterfm/milano-cortina-2026-olympic-winter-games"
    #dataset_slug = "piterfm/paris-2024-olympic-summer-games" # testing
    api.dataset_download_files(dataset_slug, path='./data', unzip=True)

def update_log(data_dir):
    """
    Updates the daily player score json.    
    Will overwrite every day's score as necessary.
    """
    events_df = pd.read_csv(data_dir + '/events.csv')    
    roster_df = pd.read_csv(data_dir + '/roster.csv')
    medallists_df = pd.read_csv(data_dir + '/medallists.csv')  

    # Create the composite keys
    medallists_df['lookup_key'] = medallists_df['discipline'] + "|" + medallists_df['event_name']
    events_df['lookup_key'] = events_df['discipline'] + "|" + events_df['event'] 
    
    # Aggregate athlete names into a list and keep the first instance of everything else
    group_cols = ['date', 'country', 'lookup_key', 'medal', 'event_name'] 
    collapsed_medals = medallists_df.groupby(group_cols).agg({
        'name': list,           # Collect names into a Python list
        'discipline': 'first'   # Keep the discipline for mapping
    }).reset_index()

    # Create the "Formatted Names" for the News Feed
    def format_winners(names):
        if len(names) == 1:
            return f"**{names[0]}**"
        elif len(names) == 2:
            return f"**{names[0]} and {names[1]}**"
        else:
            # Oxford Comma: "Name A, Name B, and Name C"
            return f"**{', '.join(names[:-1])}, and {names[-1]}**"
    collapsed_medals['winner_display'] = collapsed_medals['name'].apply(format_winners)
    
    # Apply JSON Mapping (Maps Kaggle Key -> Local Key)
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)
        collapsed_medals['lookup_key'] = collapsed_medals['lookup_key'].replace(mapping)

    # Merge on the composite key
    results = collapsed_medals.merge(
        events_df.drop(columns=['discipline']), 
        on='lookup_key', 
        how='left'
    )

    # 3. Check for missing
    missing_mask = results['event'].isna()
    if missing_mask.any():
        missing_data = results.loc[missing_mask, ['discipline', 'event_name']].drop_duplicates().to_dict(orient='records')
        with open(EXCEPTIONS_FILE, 'w') as f:
            json.dump(missing_data, f, indent=2)            
        print(f"⚠️  {len(missing_data)} unique events could not be mapped. See {EXCEPTIONS_FILE}")
        
        # Filter results to only matched rows
        results = results.dropna(subset=['base_score'])
    else:
        # If no missing events, clear the exceptions file if it exists
        if os.path.exists(EXCEPTIONS_FILE):
            os.remove(EXCEPTIONS_FILE)

    results = results.merge(roster_df, left_on='country', right_on='country')

    # This is better for the news feed
    results['medal'] = results['medal'].replace({
        "GOLD": "Gold Medal",
        "SILVER": "Silver Medal",
        "BRONZE": "Bronze Medal"
    })
 
    # Append calculated medal_points to each row
    medal_map = {"Gold Medal": 5.0, "Silver Medal": 3.0, "Bronze Medal": 2.0}
    results['medal_points'] = (results['medal'].map(medal_map) * results['base_score']).round(2)

    # Pre-calculate total athletes per owner (Step 4.2/4.3 helper)
    owner_total_athletes = roster_df.groupby('owner')['athletes'].sum().to_dict()

    # 3. Get a sorted list of medal dates
    results['date'] = pd.to_datetime(results['date'])
    unique_dates = sorted(results['date'].unique())

    score_log = []

    # 4. Calculate scores for each date snapshot
    for current_date in unique_dates:
        # Filter data up to the current loop date (running total)
        current_results = results[results['date'] <= current_date]
        
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
    medal_emojis = {
        'Gold Medal': '🥇',
        'Silver Medal': '🥈',
        'Bronze Medal': '🥉'
    }
    medal_order = ['Gold Medal', 'Silver Medal', 'Bronze Medal']
    results['medal'] = pd.Categorical(results['medal'], categories=medal_order, ordered=True)
    sorted_results = results.sort_values(
        by=['date', 'event', 'medal'], 
        ascending=[False, True, True]
    )

    # Mapping of IOC (3-letter) to ISO (2-letter) for 2026 Winter Olympic Nations
    IOC_MAPPING = {
        # North America
        'USA': 'US', 'CAN': 'CA', 'MEX': 'MX', 'PUR': 'PR', 'JAM': 'JM', 'TTO': 'TT', 'HAI': 'HT',
        # Europe (The Heavy Hitters)
        'NOR': 'NO', 'GER': 'DE', 'AUT': 'AT', 'SUI': 'CH', 'SWE': 'SE', 'FRA': 'FR', 'ITA': 'IT',
        'NED': 'NL', 'FIN': 'FI', 'GBR': 'GB', 'BEL': 'BE', 'CZE': 'CZ', 'SVK': 'SK', 'SLO': 'SI',
        'POL': 'PL', 'LAT': 'LV', 'EST': 'EE', 'LTU': 'LT', 'UKR': 'UA', 'HUN': 'HU', 'DEN': 'DK',
        'POR': 'PT', 'ESP': 'ES', 'GRE': 'GR', 'ISL': 'IS', 'IRL': 'IE', 'LUX': 'LU', 'ROU': 'RO',
        'BUL': 'BG', 'CRO': 'HR', 'SRB': 'RS', 'MNE': 'ME', 'MKD': 'MK', 'ALB': 'AL', 'AND': 'AD',
        'MON': 'MC', 'LIE': 'LI', 'SMR': 'SM', 'BIH': 'BA', 'GEO': 'GE', 'ARM': 'AM', 'AZE': 'AZ',
        # Asia
        'CHN': 'CN', 'JPN': 'JP', 'KOR': 'KR', 'PRK': 'KP', 'TPE': 'TW', 'HKG': 'HK', 'KAZ': 'KZ',
        'UZB': 'UZ', 'KGZ': 'KG', 'MGL': 'MN', 'IRI': 'IR', 'ISR': 'IL', 'TUR': 'TR', 'LBN': 'LB',
        'IND': 'IN', 'PAK': 'PK', 'THA': 'TH', 'PHI': 'PH', 'MAS': 'MY', 'SGP': 'SG', 'KSA': 'SA',
        # Oceania
        'AUS': 'AU', 'NZL': 'NZ',
        # South America
        'BRA': 'BR', 'ARG': 'AR', 'CHI': 'CL', 'COL': 'CO', 'ECU': 'EC', 'PER': 'PE', 'BOL': 'BO',
        'VEN': 'VE',
        # Africa
        'RSA': 'ZA', 'NGR': 'NG', 'GHA': 'GH', 'KEN': 'KE', 'ERI': 'ER', 'MAD': 'MG', 'MAR': 'MA',
        # Special Cases
        'AIN': 'UN',  # Individual Neutral Athletes (renders a neutral flag)
        'EOR': 'UN',  # Refugee Olympic Team
    }

    def get_flag(ioc_code):
        # Convert 3-letter to 2-letter, default to 'UN' if not found
        iso_code = IOC_MAPPING.get(ioc_code.upper(), 'UN')
        # Emoji math for 2-letter codes
        return "".join(chr(127397 + ord(c)) for c in iso_code)

    for _, row in sorted_results.iterrows():
        m_emoji = medal_emojis.get(row['medal'], '🏅')
        f_emoji = get_flag(row['code']) # Assumes 'country' is 2-letter code like 'US'
        
        entry_text = (
            f"{m_emoji} {f_emoji} {row['winner_display']} "
            f"(**{row['country']},** {row['athletes']} athletes) takes **{row['medal']}** "
            f"in {row['event']}, winning **{row['owner']}** {row['medal_points']:.2f} points!"
        )

        news_feed.append({
            "date": row['date'].strftime("%b %d, %Y"),
            "entry": entry_text,
            "owner": row['owner']
        })

    # Create per-country event breakdown for the Nation Detail tab
    country_events = {}
    for _, row in results.iterrows():
        country = row['country']
        if country not in country_events:
            country_events[country] = []
        country_events[country].append({
            "date": row['date'].strftime("%b %d, %Y"),
            "event": row['event'],
            "discipline": row['discipline'],
            "medal": row['medal'],
            "base_score": float(row['base_score']),
            "is_team": bool(row['is_team']),
            "is_prestige": bool(row['is_prestige']),
            "medal_points": float(row['medal_points']),
            "flag": get_flag(row['code'])
        })

    # Create the "Medal Table" entries (Country-level breakdown)
    medal_breakdown = results.groupby('country').agg(
        golds=('medal', lambda x: (x == 'Gold Medal').sum()),
        silvers=('medal', lambda x: (x == 'Silver Medal').sum()),
        bronzes=('medal', lambda x: (x == 'Bronze Medal').sum()),
        medal_points=('medal_points', 'sum'),
        athletes=('athletes', 'first'),
        owner=('owner', 'first')
    )
    medal_breakdown['pa_score'] = (medal_breakdown['medal_points'] / medal_breakdown['athletes']).round(2)
    
    # Merge with roster_df (and handle potential duplicate columns) to capture countries w/o medals
    final_table = roster_df.merge(
        medal_breakdown.reset_index(), 
        left_on='country',
        right_on='country',
        how='left',
        suffixes=('', '_drop') # Use suffixes=(None, '_drop') so original columns stay as-is
    ).fillna(0)

    # Drop any duplicate columns that popped up during merge
    final_table = final_table.drop(columns=[c for c in final_table.columns if '_drop' in c])
    final_table['flag'] = final_table['code'].apply(get_flag)

    medal_table_data = final_table.to_dict(orient='records')

    # Combine everything into one master file
    dashboard_data = {
        "history": score_log, # Your existing time-series data
        "medal_table": medal_table_data,
        "news": news_feed,
        "country_events": country_events
    }

    with open('dashboard_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✅ dashboard_data.json updated with {len(unique_dates)} dates.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Milano 2026 Score Updater")
    
    # Using a positional argument with specific choices
    parser.add_argument(
        'mode', 
        choices=['mock', 'local', 'pull'], 
        help="Run mode: 'mock' (test data), 'local' (process existing data), or 'pull' (fetch & process)"
    )
    
    args = parser.parse_args()

    if args.mode == 'mock':
        print("🛠️  MOCK MODE: Skipping Kaggle, using ./mock_data")
        update_log('./mock_data')

    elif args.mode == 'local':
        print("🏠 LOCAL MODE: Processing existing files in ./data (No Kaggle hit)")
        if not os.path.exists('./data'):
            print("❌ Error: ./data directory not found. Run with 'pull' first.")
        else:
            update_log('./data')

    elif args.mode == 'pull':
        print("🚀 PULL MODE: Fetching live data from Kaggle...")
        try:
            pull_data()
            print("✅ Data download complete.")
        except Exception as e:
            print(f"❌ Kaggle Pull Failed: {e}")
        update_log('./data')