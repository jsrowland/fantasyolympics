import pandas as pd
import numpy as np
import os

EVENTS_PATH = 'data/events.csv'

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
    df['base_score'] = df['base_score'].clip(upper=max_base_score)

    # Multiplies by 4 where 'is_team' is True, else multiplies by 1 (no change)
    df['base_score'] *= np.where(df['is_team'], 4, 1)
    
    # Multiplies by 3 where 'is_prestige' is True, else multiplies by 1
    df['base_score'] *= np.where(df['is_prestige'], 3, 1)

    df['base_score'] = df['base_score'].round(2)
    
    # Clean up the helper column
    return df.drop(columns=['events_in_discipline'])

events_df = pd.read_csv(EVENTS_PATH)
name, ext = os.path.splitext(EVENTS_PATH)
events_df.to_csv(name + '_backup' + ext)
events_df = set_base_scores(events_df)
events_df.to_csv(EVENTS_PATH)