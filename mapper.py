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
    print(f"✅ Mapping saved to {MAPPING_FILE}")

def run_mapper(mode):
    # 1. Load Reference Data
    if not os.path.exists(EVENTS_CSV):
        return print(f"❌ Error: {EVENTS_CSV} not found.")
    
    local_df = pd.read_csv(EVENTS_CSV)
    local_df['key'] = local_df['discipline'] + "|" + local_df['event']
    local_keys = local_df['key'].tolist()
    
    mapping = load_json(MAPPING_FILE)
    to_process = []

    # 2. Select Source based on CLI Argument
    if mode == 'schedule':
        if not os.path.exists(SCHEDULE_CSV):
            return print(f"❌ Error: {SCHEDULE_CSV} not found.")
        sched_df = pd.read_csv(SCHEDULE_CSV)
        # Only medal events; normalize keys
        medal_events = sched_df[sched_df['event_medal'] == 1][['discipline', 'event']].drop_duplicates()
        for _, row in medal_events.iterrows():
            to_process.append({'discipline': row['discipline'], 'event': row['event']})
        print(f"📋 Mode: Schedule (Processing {len(to_process)} medal events)")

    elif mode == 'missing':
        missing_data = load_json(EXCEPTIONS_FILE)
        if not missing_data:
            return print(f"✅ No missing events found in {EXCEPTIONS_FILE}.")
        for item in missing_data:
            # Main script uses discipline_x and event_name
            to_process.append({'discipline': item['discipline_x'], 'event': item['event_name']})
        print(f"📋 Mode: Missing (Processing {len(to_process)} exceptions)")

    # 3. Pass 1: Auto-Mapping (Exact matches)
    auto_count = 0
    remaining = []
    for item in to_process:
        k_key = f"{item['discipline']}|{item['event']}"
        if k_key in mapping:
            continue
        if k_key in local_keys:
            mapping[k_key] = k_key
            auto_count += 1
        else:
            remaining.append(item)

    if auto_count > 0:
        print(f"🤖 Auto-mapped {auto_count} exact matches.")

    # 4. Pass 2: Interactive Mapping
    if not remaining:
        save_mapping(mapping)
        return

    print(f"\n--- {len(remaining)} events require manual mapping ---")
    for item in remaining:
        k_name, k_disc = item['event'], item['discipline']
        k_key = f"{k_disc}|{k_name}"

        print(f"\nTarget: **{k_name}** ({k_disc})")

        # 1. Filter local choices by discipline
        disc_matches = local_df[local_df['discipline'].str.contains(k_disc, case=False, na=False)].copy()
        if disc_matches.empty:
            disc_matches = local_df.copy()

        # 2. Generate Fuzzy Suggestions
        guesses = difflib.get_close_matches(k_name, disc_matches['event'].tolist(), n=3, cutoff=0.2)
        
        # 3. Reorder: Pull guesses to the top
        # Create a 'priority' dataframe for guesses and 'others' for the rest
        priority_df = disc_matches[disc_matches['event'].isin(guesses)].copy()
        # Sort priority_df to match the order of 'guesses' (best match first)
        priority_df['sort_order'] = priority_df['event'].apply(lambda x: guesses.index(x))
        priority_df = priority_df.sort_values('sort_order')
        
        others_df = disc_matches[~disc_matches['event'].isin(guesses)]
        
        # Combine them: Suggestions first, then the rest
        final_selection_df = pd.concat([priority_df, others_df])
        
        options = (final_selection_df['event'] + " (" + final_selection_df['discipline'] + ")").tolist()
        option_keys = final_selection_df['key'].tolist()

        # 4. Display
        print(f"--- Top Suggestions ---")
        for i, opt in enumerate(options):
            if i == len(guesses):
                print(f"--- All Other {k_disc} Events ---")
            
            # Highlight the top guesses to make them pop
            prefix = "⭐ " if i < len(guesses) else "  "
            print(f"{prefix}{i}: {opt}")

        choice = input(f"\nSelect index for '{k_name}' (or Enter to skip): ").strip()
        
        if choice.isdigit() and int(choice) < len(option_keys):
            mapping[k_key] = option_keys[int(choice)]
            print(f"✅ Linked to: {option_keys[int(choice)]}")

    save_mapping(mapping)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Olympic Event Mapper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--schedule', action='store_const', const='schedule', dest='mode')
    group.add_argument('--missing', action='store_const', const='missing', dest='mode')
    
    args = parser.parse_args()
    run_mapper(args.mode)