import pandas as pd
import json
import os
import argparse
import difflib

# Configuration
MAPPING_FILE = 'event_mapping.json'
EXCEPTIONS_FILE = 'missing_events.json'
EVENTS_CSV = './data/events.csv'
SCHEDULE_CSV = './data/schedules.csv'

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {} if "mapping" in filepath else []

def save_mapping(mapping):
    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"\n✅ Mapping saved to {MAPPING_FILE}")

def run_mapper(mode):
    if not os.path.exists(EVENTS_CSV):
        return print(f"❌ Error: {EVENTS_CSV} not found.")
    
    # 1. Load Local Events & Current Mapping
    local_df = pd.read_csv(EVENTS_CSV)
    local_df['key'] = local_df['discipline'] + "|" + local_df['event']
    
    mapping = load_json(MAPPING_FILE)
    to_process = []

    # 2. Identify "Used" Local Events (Values in our mapping)
    used_local_keys = set(mapping.values())

    # 3. Choose Source
    if mode == 'schedule':
        if not os.path.exists(SCHEDULE_CSV): return print("❌ schedules.csv missing.")
        sched_df = pd.read_csv(SCHEDULE_CSV)
        medal_events = sched_df[sched_df['event_medal'] == 1][['discipline', 'event']].drop_duplicates()
        to_process = [{'discipline': r['discipline'], 'event': r['event']} for _, r in medal_events.iterrows()]
    else:
        missing_data = load_json(EXCEPTIONS_FILE)
        if not missing_data: return print("✅ No missing events found.")
        to_process = [{'discipline': i['discipline_x'], 'event': i['event_name']} for i in missing_data]

    # 4. Pass 1: Auto-Mapping (Exact Matches in pool)
    remaining = []
    for item in to_process:
        k_key = f"{item['discipline']}|{item['event']}"
        if k_key in mapping: continue
        
        # If exact match exists AND hasn't been used yet
        if k_key in local_df['key'].values and k_key not in used_local_keys:
            mapping[k_key] = k_key
            used_local_keys.add(k_key)
        else:
            remaining.append(item)

    # 5. Pass 2: Interactive Reordered Mapping
    for item in remaining:
        k_name, k_disc = item['event'], item['discipline']
        k_key = f"{k_disc}|{k_name}"
        if k_key in mapping: continue

        print(f"\nTarget: **{k_name}** ({k_disc})")

        # FILTER: Only show events NOT already in used_local_keys
        available_df = local_df[~local_df['key'].isin(used_local_keys)].copy()
        
        # Priority Filter: Same discipline
        disc_pool = available_df[available_df['discipline'].str.contains(k_disc, case=False, na=False)].copy()
        if disc_pool.empty: disc_pool = available_df # Fallback

        # Fuzzy Suggestions
        guesses = difflib.get_close_matches(k_name, disc_pool['event'].tolist(), n=3, cutoff=0.2)
        
        # Reorder Pool: Suggestions First
        priority_df = disc_pool[disc_pool['event'].isin(guesses)].copy()
        if not priority_df.empty:
            priority_df['sort'] = priority_df['event'].apply(lambda x: guesses.index(x))
            priority_df = priority_df.sort_values('sort')
        
        others_df = disc_pool[~disc_pool['event'].isin(guesses)]
        final_selection_df = pd.concat([priority_df, others_df])

        options = (final_selection_df['event'] + " (" + final_selection_df['discipline'] + ")").tolist()
        option_keys = final_selection_df['key'].tolist()

        print(f"--- Available Options ({len(options)} left in discipline) ---")
        for i, opt in enumerate(options):
            prefix = "⭐ " if i < len(guesses) else "   "
            if i == len(guesses): print("-----------------------")
            print(f"{prefix}{i}: {opt}")

        choice = input(f"\nMatch index for '{k_name}' (Enter to skip): ").strip()
        
        if choice.isdigit() and int(choice) < len(option_keys):
            selected_key = option_keys[int(choice)]
            mapping[k_key] = selected_key
            used_local_keys.add(selected_key) # IMMEDIATELY remove from next loop's pool
            print(f"Linked!")

    save_mapping(mapping)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--schedule', action='store_const', const='schedule', dest='mode')
    group.add_argument('--missing', action='store_const', const='missing', dest='mode')
    run_mapper(parser.parse_args().mode)