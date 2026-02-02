import os
from dotenv import load_dotenv
load_dotenv()
import kaggle # imports creds on import so load_dotenv first
import pandas as pd

# 1. AUTHENTICATE
# This assumes your kaggle.json is in ~/.kaggle/
kaggle.api.authenticate()

# 2. DOWNLOAD DATASET
# This grabs the specific 2026 folder and unzips it for you
dataset_slug = "piterfm/milano-cortina-2026-olympic-winter-games"
kaggle.api.dataset_download_files(dataset_slug, path='./data', unzip=True)

# 3. READ THE GOOD STUFF
# 'results.csv' is where the magic happens during the Games
#results_df = pd.read_csv('./data/results.csv')
schedules_df = pd.read_csv('./data/schedules.csv')