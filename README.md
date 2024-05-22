### Adult League Hockey Stats


My beer league hockey team had the same problem a lot of other teams have. The rink only displays player statistics one season at a time, but a lot of us want to know how our stats look for our entire careers. 

We also want to know how our team stacks up against the team we’re playing against. We want to know things like how our goal differentials compare, who has the better goalie, and who their leading scorers are. 
To solve these problems, we created a python script that scrapes career statistics for all players going back to 2007 and plugs the dataset into Power BI. The dashboard is saved in Power BI workspace here:

https://app.powerbi.com/groups/me/reports/a6c8c1e2-637e-4d37-ab5d-3fb87544ebc6/ReportSection?experience=power-bi

![image](https://github.com/chrismca13/HockeyStats/assets/40841565/a58c74ce-300d-456e-a1a1-611dc553853f)

Overview of files:

* **GangGreenStats_ThisSeason.py**: Gets all the team, goalie, and individual stats for a single division, and updates a local CSV that my Power BI dashboard is pointed toward (saved in Output_data folder).
* **OaklandHockey_Payer_AllTime.py**: Gets the individual player stats for a single division going back to 2007 and updates a CSV.
* **Oakland Hockey Scouting Report.pbi**: Power BI workbook that contains individual all time stats and team scouting reports.
* **Oakland Gang Green Hockey Stats.twb**: Tableau dashboard simialr to the PBI one. Currently uploaded to Tableau public.

**To Refresh current year data:**
* cd Documents\GitHub\HockeyStat
* py .\GangGreenStats_ThisSeason.py
