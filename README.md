## Adult League Hockey Stats

My beer league hockey team had the same problem a lot of other teams have. The rink only displays player statistics one season at a time, but a lot of us want to know how our stats look for our entire careers. 

To solve this problem, I created a web app that tracks our stats going back 15+ years:
[https://oakhockey.streamlit.app/](https://oakhockey.streamlit.app/)

#### Summary of Process
1. The Oakland Ice Center tracks player stats for every division on their [website](https://stats.sharksice.timetoscore.com/display-stats.php?league=27).
* They also track stats going back several years, which can be accessed by adjusting the `season=` parameter in the URL.
2. We iterate over the seasons, storing everyone's stats in a data frame.
3. We store that data in the s3 path defined in the `data_refresh/config.json`. The default path is below, which has public read access:
* `"s3://gang-green-hockey/ALL_OaklandHockeyData.csv"`
* Steps 1-3 only run when the `TOTAL_REFRESH` parameters in `data_refresh/config.json` is set to `TRUE`. This needs to be done at the start of the season. 
* We also need to update the `Input_data/OaklandHockeySeasonDim.csv` file with the new season identifier.

4. If `TOTAL_REFRESH` is set to `FALSE` (which is the default), then the following process runs every Wednesday morning:
* Read in the data stored in the s3 path under `CURRENT_BUCKET_PATH` in `data_refresh/config.json`. The default is `s3://gang-green-hockey/ALL_OaklandHockeyData.csv`. 
* We delete the current season's data, and replace it with up to date stats as of the refresh date. All this happens in the `update_current_season()` function.
* We aggregate the data from player-date grain up to the player grain, summarizing most statistics by summing. This happens in the `data_manip()` function.
* Lastly, we upload the data to the s3 path in the `config.json`, supplied by the `NEW_FILE_NAME` parameter. The default path is `"s3://gang-green-hockey/ALL_OaklandHockeyData_CURRENT.csv"`
5. Step 4 runs every Wednesday morning, and the web app consumes the data directly from  `"s3://gang-green-hockey/ALL_OaklandHockeyData_CURRENT.csv"`




Overview of files:
```
├── app/
│   ├── app.py           # Streamlit web app for interactive stats visualization
│   └── test.ipynb       # Notebook for app development/testing
├── data_refresh/
│   ├── __init__.py      # Package init
│   ├── config.json      # Configuration for data refresh pipeline
│   ├── data_manip.ipynb # Notebook for data manipulation
│   ├── helpers.py       # Utility functions for S3, web scraping, and data processing
│   ├── README.md        # Data refresh pipeline documentation
├── main.py              # Main script to run the data refresh pipeline
├── requirements.txt     # Python dependencies for all scripts and the app
```

## Main Components

### Data Refresh Pipeline
- **main.py**: Orchestrates the data refresh process. Reads config, pulls/updates stats, processes data, and uploads results to S3.
- **data_refresh/helpers.py**: Contains functions for S3 upload, web scraping, updating current season, and data manipulation.
- **data_refresh/config.json**: Stores pipeline settings (S3 paths, file names, division mapping, etc).
- **data_refresh/data_manip.ipynb**: Notebook for exploring and transforming raw data.

### Web App
- **app/app.py**: Streamlit app for visualizing player stats. Features:
  - Filter and sort stats by team, player, and stat sliders
  - Interactive scatter plot (Games Played vs Points)
  - Responsive table of player stats
- **app/test.ipynb**: Notebook for prototyping app features.

### Supporting Files
- **requirements.txt**: Lists all required Python packages (Streamlit, pandas, s3fs, fsspec, plotly, boto3).
