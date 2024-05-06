# ### Oakland Gang Green Hockey All Time Stats
# Chris McAllister
 
# This script gathers all the Oakland Hockey Stats for all 4 GG teams, for every season that which the website has data.
 
# Oultine:

# 1) Import libraries
# 2) Establish mapping of GG Team ID's in URL to Team Names (Gang Green 1, 2, etc.)

# 3/4) Get a base dataset of all the players who played for Gang Green in our season dim range
# 3/4) Read in a CSV that converts SeasonIDs to the Season Name
#  5) Light data manipulation. Removing columns, create Points per Game metric, etc.

# 1) Import libraries
import pandas as pd
from datetime import datetime
today = datetime.today().strftime('%Y-%m-%d')

# Ignore any warning messages
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import filterwarnings
filterwarnings('ignore')

# 2) Create simple mapping table that converts the Team ID to a Team Name.
def create_team_dim_table(team_ids, team_names):
    """
    Arguments:
    team_ids (list): a list of team ids. These numbers are how the website defines our team. For example, Gang Green2 has a team id #692 on the stats website. 
    team_names (list): a list of team names in the same order as the team ids

    This function zips the two lists together and returns a dataframe that we will later use to create our final dataset. 
    """

    team_dim_df = pd.DataFrame(zip(gg_team_ids, gg_team_names), columns = ['TeamID', 'Team Name'])
    return team_dim_df

gg_team_ids = [1843, 692, 4622, 4818]
gg_team_names = ['Gang Green 1', 'Gang Green 2', 'Gang Green 3', 'Gang Green 4']
team_dim = create_team_dim_table(gg_team_ids, gg_team_names)


# 3/4) Get a base dataset of all the players who played for Gang Green in our season dim range
def base_web_data(team_ids, season_dim_csv):

    """
    This function takes in two arguments:

    team_ids (list): List ot integers referencing the IDs of the teams we're interested in pulling.
                     Gang Green's are manually supplied below.
    season_dim_csv (csv): A csv that acts as a dimensional table for all the seasons we want to pull in.
                          One row is one season. Key is the ID of that season according to the website
                          Other attributes includes the year, season name (Fall 2021, eg.), etc.

    returns a dataframe that is at the player-season grain of all GG players that played in a season in our season_dim_csv file. 
    
    """


    # Establish empty df  of our columns
    df_main = pd.DataFrame(columns = ['Name', '#', 'GP', 'Goals', 'Ass.', 'PPG', 'PPA', 'SHG', 'SHA', 'GWG',
        'GWA', 'PSG', 'ENG', 'UAG', 'IG', 'IA', 'TG', 'TA', 'FG', 'SOG', 'SOA',
        'Shots', 'PIMs', '+/-', 'Hat', 'Pts'])

    # For each GG team, loop over every season to grab their stats and append it to our big dataframe we made above.
    # This is written very inefficiently and will be pretty slow. 

    # season dim dataframe
    # season_dim = pd.read_csv('OaklandHockeySeasonDim.csv')

    for team_id in team_ids:

        for season_id in season_dim_csv['SeasonID']:
            url = 'https://stats.sharksice.timetoscore.com/display-schedule?team='+str(team_id)+'&season=' + str(season_id) + '&league=27&stat_class=1'

            # There are gaps in season IDs (for example there's no season #34). 
            # This would cause an error when reading the URL so we need to handle that with the try / except code block below. 
            try:
                df = pd.read_html(url)
                # Remove first layer of column (that just say says 'Game Results')
                #df[0].columns = df[0].columns.droplevel()
                #df[0].head()

                df[1].columns = df[1].columns.droplevel()
                df[1]['SeasonID'] = int(season_id)
                df[1]['TeamID'] = int(team_id)
                

                df_main = pd.concat([df_main, df[1]])
                #df_main['SeasonID'] = season_id

            except:
                pass

    return df_main

# 4) Read in a CSV that converts SeasonIDs to the Season Name
season_dim = pd.read_csv('OaklandHockeySeasondDim.csv')
df_main = base_web_data(gg_team_ids, season_dim)


# 5) Light data manipulation. Removing columns, create Points per Game metric, etc.
def data_manip(df):

    """
    Argument(s):
    A df at the grain of player-season.
    It it the outuput of the previous function call base_web_data()

    returns a manipulated df where a player's stats are aggregated to the player grain. 
    """

    # Cast as integers so the join below works (otherwise it won't recognize 5.0 as 5, etc.)
    df['SeasonID'] = df['SeasonID'].astype(int) 
    df['TeamID'] = df['TeamID'].astype(int)
    # Convert season IDs (#40) to Season Name (Fall 2017)
    df_final = pd.merge(left = df, right = season_dim, how = 'left', left_on = 'SeasonID', right_on = 'SeasonID')

    # Only select necessarry columns
    col = ['Name', '#', 'GP', 'Goals', 'Ass.', 'PPG', 'PPA', 'SHG', 'SHA', 'GWG',
        'GWA', 'PSG', 'ENG',  'PIMs', 'Hat', 'Pts', 'SeasonID', 'Season', 'Year', 'TeamID',
        'SeasonName']

    df_final = df_final[col]

    # Create a GPG and Pts per game metric. 
    df_final['GPG'] = df_final['Goals'] / df_final['GP']
    df_final['Pts_PG'] = df_final['Pts'] / df_final['GP']

    df_final['SeasonID'] = df_final['SeasonID'].astype(int) 
    df_final['TeamID'] = df_final['TeamID'].astype(int)
    
    # Get team name from Team ID (GG 1, 3, etc.)
    manip_df = pd.merge(left = df_final, right = team_dim, how = 'left', left_on = 'TeamID', right_on = 'TeamID')
    manip_df['lastupdated'] = datetime.today().strftime('%Y-%m-%d')

    # Ouput results to CSV
    manip_df.to_csv('OaklandHockeyData.csv', index = False)

    return manip_df


# data_manip(df_main)
