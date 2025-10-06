import boto3
from io import StringIO
import pandas as pd
import numpy as np
import os
from io import StringIO
import boto3
from datetime import datetime
import s3fs
import fsspec
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import filterwarnings

today = datetime.today().strftime('%Y-%m-%d')


def upload_df_to_s3(df: pd.DataFrame, bucket_name: str, new_file_name: str, region: str = "us-east-2"):
    """
    Uploads a pandas DataFrame to S3 as a CSV.

    Parameters:
    - df: pandas DataFrame to upload
    - bucket_name: S3 bucket name
    - new_file_name: Key/path in the S3 bucket (e.g., 'folder/file.csv')
    - region: AWS region (default 'us-east-2')
    """

    # Convert DataFrame to CSV in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)


    # Upload using boto3 with ACL and error handling
    s3 = boto3.client("s3", region_name=region)
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=new_file_name,
            Body=csv_buffer.getvalue(),
            ACL="bucket-owner-full-control"
        )
        print(f"New data now available in {bucket_name} with name: {new_file_name}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")



# 2) Get a base dataset of all the players who played for Gang Green in our season dim range
# This needs to be run occasionally, when a new season starts. Upload it to S3 when done.
def initial_web_data(season_dim_csv, s3_current, new_file_name, div_dict, bucket_name):

    """
    Loops over every season in our season_dim_csv file, and every division in our div_dict dictionary.

    This function takes in one arguments:

    season_dim_csv (csv): A csv that acts as a dimensional table for all the seasons we want to pull in.
                          One row is one season. Key is the ID of that season according to the website
                          Other attributes includes the year, season name (Fall 2021, eg.), etc.
                          Needs to be updated once per season

    returns a dataframe that is at the player-season grain of all GG players that played in a season in our season_dim_csv file. 
    """

    print('Running For every season and division')
    
    # Establish empty df  of our columns
    df_main = pd.DataFrame(columns = ['Name', '#', 'Team', 'GP', 'Goals', 'Ass.', 'Hat', 'Min', 'Pts/Game', 'Pts'])

    # May need to change this if the league adds a new division
    for index, season_id in enumerate(season_dim_csv['SeasonID']):
        for league_id in list(div_dict.keys()):

            url = 'https://stats.sharksice.timetoscore.com/display-league-stats?stat_class=1&league=27&season=' + str(season_id) + '&level=' + str(league_id) + '&conf=0'

            # There are gaps in season IDs (for example there's no season #34). 
            # This would cause an error when reading the URL so we need to handle that with the try / except code block below. 
            try:
                df = pd.read_html(url)
                df[0].columns = df[0].columns.droplevel()
                df[0]['SeasonID'] = int(season_id)
                df[0]['division'] = str(div_dict[league_id])

                df_main = pd.concat([df_main, df[0]])

            except:
                print('Season ID: ' + str(season_id) + ' Division ID: ' + str(league_id) + ' does not exist. Skipping...')
                print(url)

        if index % 3 == 0:
            print(f'Processed {index} seasons so far')

    # Write to S3, hard coded!
    upload_df_to_s3(df_main, "gang-green-hockey", "ALL_OaklandHockeyData.csv")



def update_current_season(s3_path, div_dict):
    """
    This function updates the dataset in S3 with the latest data. 
    Should be run every day to get last night's stats from the league website.

    It reads in the big dataset with all the historical data, drops the current season, then re-reads the current season from the website
    and appends it to the historical data.
    """

    df = pd.read_csv(s3_path)

    max_season = df['SeasonID'].max()

    df_drop_curr_season = df[df['SeasonID'] != max_season]

    # May need to change this if the league adds a new division
    for league_id in list(div_dict.keys()):

        url = 'https://stats.sharksice.timetoscore.com/display-league-stats?stat_class=1&league=27&season=' + str(int(max_season)) + '&level=' + str(league_id) + '&conf=0'

        # There are gaps in season IDs (for example there's no season #34). 
        # This would cause an error when reading the URL so we need to handle that with the try / except code block below. 
        try:
            df_curr = pd.read_html(url)
            df_curr[0].columns = df_curr[0].columns.droplevel()
            df_curr[0]['SeasonID'] = int(max_season)
            df_curr[0]['division'] = str(div_dict[league_id])

            df_drop_curr_season = pd.concat([df_drop_curr_season, df_curr[0]])

        except:
            print('Division ID: ' + str(league_id) + ' does not exist. Skipping...')
            print(url)
    
    return df_drop_curr_season



def data_manip(df, season_dim):

    """
    Basic data manipulation function - converts dimensional columns to names, renames columns, drops old columns.
    Also returns a df at the player grain, rather than player-season. 

    Argument(s):
    A df at the grain oaf player-season.
    The outuput of the previous function call base_web_data()

    returns a manipulated df with a few extra columns
    """
    df_final = pd.merge(left = df, right = season_dim, how = 'left', left_on = 'SeasonID', right_on = 'SeasonID')

    # Only select necessarry columns
    col = ['Name', '#', 'Team', 'GP', 'Goals', 'Ass.', 'Hat', 'Min', 'Pts/Game', 'Pts', 'SeasonName', 'SeasonID', 'Year']

    df_final = df_final[col]
    df_final['SeasonID'] = df_final['SeasonID'].astype(int) 
    df_final['Year'] = df_final['Year'].astype(int) 
    df_final['Most Recent Season'] = df_final['Year']

    df_primary_team = df_final.copy()

    df_primary_team = df_primary_team.groupby(by = ['Name', 'Team'], as_index = False)\
                                     .agg({'GP': 'sum'})\
                                     .rename({'GP':'Primary Team GP'}, axis = 1)

    # Identify Primary team defined by what team they played more games for
    df_primary_team['rn'] = df_primary_team.sort_values(['Name', 'Team', 'Primary Team GP'], ascending=[True, True, False]) \
                                           .groupby(['Name']) \
                                           .cumcount() + 1
    
    df_primary_team = df_primary_team[df_primary_team['rn'] == 1]
    df_primary_team = df_primary_team.drop(columns = 'rn', axis = 1)


    df_final = df_final.groupby(by = 'Name', as_index = False).agg({'GP':'sum',
                                                                    'Goals':'sum',
                                                                    'Ass.': 'sum',
                                                                    'Hat':'sum',
                                                                    'Min': 'sum',
                                                                    'Pts': 'sum',
                                                                    'Most Recent Season':'max'})
    
    df_final = pd.merge(left = df_final, right = df_primary_team, how = 'left', on = 'Name')


    return df_final