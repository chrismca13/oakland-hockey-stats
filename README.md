### Adult League Hockey Stats

My beer league hockey team had the same problem a lot of other teams have. The rink only displays player statistics one season at a time, but a lot of us want to know how our stats look for our entire careers. 

To solve this problem, I created a web app that tracks our stacks going back 15+ years:
[https://oakhockey.streamlit.app/](https://oakhockey.streamlit.app/)

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
