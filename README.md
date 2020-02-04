# Coronavirus Notification System

This script is meant to routinely check on the Center of Disease Control's database on Coronavirus cases. I have filtered the data down to illinois. If there are any new cases, the script sends an email via smpt with a quick report.

Schedule this script in Windows Scheduler or as a chron job to always stay up to date.

The only thing required is a google account. The Socrata account is optional, though without it your requests will be limited.

Find info on setting up the Socrata API [here](https://dev.socrata.com/foundry/data.cdc.gov/x8jf-txib)
