import pandas as pd

def sync_athlete_counts():
    # Load the files
    roster_path = './data/roster.csv'
    athletes_path = './data/athletes.csv'
    
    roster_df = pd.read_csv(roster_path)
    athletes_df = pd.read_csv(athletes_path)

    # 1. Count athletes per country code
    # This creates a Series where index is code and value is the count
    athlete_counts = athletes_df['country_code'].value_counts().reset_index()
    athlete_counts.columns = ['code', 'athletes']

    # 2. Join with roster
    # 'left' join ensures we keep all countries in the roster even if they have 0 athletes
    updated_roster = pd.merge(
        roster_df.drop(columns=['athletes'], errors='ignore'),
        athlete_counts, 
        on='code', 
        how='left'
    ).fillna({'athletes': 0}) # Fill countries with no athletes as 0

    # 3. Convert athletes to integer (merge often makes them floats due to NaNs)
    updated_roster['athletes'] = updated_roster['athletes'].astype(int)

    # 4. Save it back
    updated_roster.to_csv(roster_path, index=False)
    print(f"✅ Successfully updated {roster_path} with athlete counts.")

if __name__ == "__main__":
    sync_athlete_counts()