import pandas as pd
import os
import json
from datetime import datetime


from data_refresh.helpers import upload_df_to_s3, update_current_season, data_manip, initial_web_data

# Load config.json 
with open("data_refresh/config.json", "r") as f:
    config = json.load(f)


TOTAL_REFRESH = config["TOTAL_REFRESH"]
SEASON_DIM_PATH = config["SEASON_DIM_PATH"]
CURRENT_BUCKET_PATH = config["CURRENT_BUCKET_PATH"]
NEW_FILE_NAME = config["NEW_FILE_NAME"]
DIVISION_DICT = config["DIVISION_DICT"]
BUCKET_NAME = config['BUCKET_NAME']

print('opened config and loaded vars')

def main():
    now = datetime.now()
    # weekday() == 2 means Wednesday (Monday=0, ..., Sunday=6)
    if not (now.weekday() == 2 and now.hour < 12):
        print("Script is only allowed to run before noon on Wednesday. Exiting.")
        return

    print('reading in season_dim')
    season_dim = pd.read_csv(SEASON_DIM_PATH)
    if TOTAL_REFRESH:
        data = initial_web_data(season_dim, CURRENT_BUCKET_PATH, NEW_FILE_NAME, DIVISION_DICT, BUCKET_NAME)

    print('running update_current_season')
    data = update_current_season(CURRENT_BUCKET_PATH, DIVISION_DICT)

    df = data_manip(data, season_dim)
    upload_df_to_s3(df, BUCKET_NAME, NEW_FILE_NAME)
    
if __name__ == "__main__":
    main()