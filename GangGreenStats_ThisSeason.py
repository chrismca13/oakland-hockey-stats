# 1) Import libraries. All we need is Pandas
import pandas as pd

# Don't truncate dataframes (ie show every column)
pd.set_option('display.max_columns', None)


# Ignore any warning messages. 
import warnings
warnings.filterwarnings('ignore')

# 2) Create simple mapping table that converts the Team ID to a Team Name.
d5_team_ids = [692, 3424, 4679, 2585, 4680, 4719, 4400]
d5_team_names = ['Gang Green 2', 'Oakland Reapers', 'Silver Bullets 2', 'No Regretzkys', 'Sofa King Old', 'Lot Lizards', 'Silver Squids']

team_dim = pd.DataFrame(zip(d5_team_ids, d5_team_names), columns = ['TeamID', 'Team Name'])


team_id_list = list(team_dim['TeamID'])
team_name_list = list(team_dim['Team Name'])

df_stats = []
df_goalies = []
df_team = []

for i in team_id_list:

    url = 'https://stats.sharksice.timetoscore.com/display-schedule?team='+str(i)+'&season=0&league=27&stat_class=1'
    
    df = pd.read_html(url)
    
    # stats
    df[1].columns = df[1].columns.droplevel()
    df[1]['TeamID'] = i
    df_stats.append(df[1])
    
    # goalies
    df[2].columns = df[2].columns.droplevel()
    df[2]['TeamID'] = i
    df_goalies.append(df[2])
    
    # team
    df[3].columns = df[3].columns.droplevel()
    df[3]['TeamID'] = i
    df_team.append(df[3])
    
df_stats_final = pd.concat(df_stats)
df_goalies_final = pd.concat(df_goalies)
df_team_final = pd.concat(df_team)

# Join to get team names from Team ID

df_stats_final = pd.merge(left = df_stats_final, right = team_dim, on = 'TeamID')
df_goalies_final = pd.merge(left = df_goalies_final, right = team_dim, on = 'TeamID')
df_team_final = pd.merge(left = df_team_final, right = team_dim, on = 'TeamID')

df_stats_final.to_csv('currentseason_stats.csv', index = False)
df_goalies_final.to_csv('currentseason_goalies.csv', index = False)
df_team_final.to_csv('currentseason_team.csv', index = False)