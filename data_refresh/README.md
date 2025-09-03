# Oakland Hockey Data Refresh Pipeline

This folder contains scripts and configuration for refreshing and updating the Oakland Hockey player stats dataset. The workflow is designed to pull the latest stats from the league website, process them, and upload the results to an AWS S3 bucket for use in dashboards and analytics.

## Files Overview

```
data_refresh/
├── config.json        # Configuration settings (paths, S3 info, division mapping)
├── helpers.py         # Utility functions for data fetching, processing, and S3 upload
├── main.py            # Main script to run the refresh/update workflow
└── README.md          # This documentation
```

- **config.json**  
  Stores configuration settings, including file paths, S3 bucket info, and division mappings. Keep 'TOTAL_REFRESH' to FALSE unless you want to pull brand new data, or it's a new season.

- **helpers.py**  
  Contains utility functions for:
  - Uploading DataFrames to S3 (`upload_df_to_s3`)
  - Pulling all player-season data from the league website (`initial_web_data`)
  - Updating the current season's stats (`update_current_season`)
  - Manipulating and aggregating the data for reporting (`data_manip`)

- **main.py**  
  Main entry point for the refresh workflow.  
  - Loads configuration from `config.json`
  - Reads the season dimension table
  - If `TOTAL_REFRESH` is true, pulls all historical data from the website
  - Always updates the current season's stats
  - Processes and aggregates the data
  - Uploads the final dataset to S3

## How to Execute

1. **Install dependencies**  
   Make sure you have Python 3 and the required packages (`pandas`, `boto3`, `s3fs`, `fsspec`, etc.) installed.

2. **Configure AWS credentials**  
   Ensure your AWS credentials are set up for `boto3` to access the S3 bucket.

3. **Run the script**  
   From the `data_refresh` directory, execute:

   ```sh
   python main.py
   ```

## Where the Data Ends Up

- The processed dataset is uploaded to the S3 bucket specified in `config.json`:
  - **Bucket:** `gang-green-hockey`
  - **Path:** `ALL_OaklandHockeyData_CURRENT.csv` (or as set in `NEW_FILE_NAME`)
- You can find or use the data at:  
  `s3://gang-green-hockey/ALL_OaklandHockeyData_CURRENT.csv`