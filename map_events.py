import pandas as pd
import json
import os

MAPPING_FILE = 'event_mapping.json'
EXCEPTIONS_FILE = 'missing_events.json'
EVENTS_CSV = './data/events.csv'

def run_mapper():
    if not os.path.exists(EXCEPTIONS_FILE):
        print("✅ No missing events found.")
        return

    with open(EXCEPTIONS_FILE, 'r') as f:
        missing_list = json.load(f)

    events_df = pd.read_csv(EVENTS_CSV)
    
    # Load existing mappings
    mapping = {}
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, 'r') as f:
            mapping = json.load(f)

    print(f"\n--- Event Mapping Tool (with Discipline Context) ---")

    for item in missing_list:
        k_name = item['event_name']
        k_disc = item['discipline_x']

        print(f"\nKaggle Event: **{k_name}**")
        print(f"Discipline:   {k_disc}")
        
        # 1. Try to narrow down events.csv by discipline
        # We use a case-insensitive match
        mask = events_df['discipline'].str.contains(k_disc, case=False, na=False)
        suggestions_df = events_df[mask]

        # If no discipline match, show everything (fallback)
        if suggestions_df.empty:
            print("! No matching discipline found in events.csv. Showing all events.")
            suggestions_df = events_df

        valid_suggestions = sorted(suggestions_df['event'].unique().tolist())

        # 2. Display suggestions
        for i, sug in enumerate(valid_suggestions):
            print(f"  {i}: {sug}")

        choice = input(f"\nMatch for '{k_name}' (Index #, Exact Name, or Enter to skip): ").strip()

        if choice == "":
            continue
        
        if choice.isdigit() and int(choice) < len(valid_suggestions):
            mapping[k_name] = valid_suggestions[int(choice)]
            print(f"Linked!")
        elif choice in events_df['event'].values:
            mapping[k_name] = choice
            print(f"Linked!")
        else:
            print(f"❌ '{choice}' not found. Skipping.")

    with open(MAPPING_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n✅ Mapping saved to {MAPPING_FILE}.")

if __name__ == "__main__":
    run_mapper()