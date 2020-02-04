from sodapy import Socrata
import datetime
import os
import sqlite3
import smtplib

### EDIT HERE ####
sender_email = "<Your Gmail>"
password = '<Gmail Password>'
receiver_email = ['email1@gmail.com','email2@gmail.com']
socrata_api= '<Your Socrata API>' # Optional
socrata_user = '<Your Socrata Email>' # Optional
socrata_passwd = '<Your Socrata Password>' # Optional
reporting_area_key = 'ILLINOIS'
##################

# Open database to keep track
conn = sqlite3.connect("./data.db")

# Download data from socrata without socrata account
client = Socrata('data.cdc.gov',None)

# Download data from socrata with socrata account
client = Socrata('data.cdc.gov',
                 socrata_api,
                 username=socrata_user,
                 password=socrata_passwd) 

# returns as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("x8jf-txib", reporting_area=reporting_area_key)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
 
# select desired columns
results_df = results_df[["reporting_area","mmwr_year","mmwr_week",'updated_on']]

# Count previous number of reports
try:
    old_count = pd.read_sql_query("select count(*) as counts from new_data",conn).counts[0]
except:
    old_count = 0 # This is why the first email will be inaccurate. You can fix this if you want.

# If new count is more, send an email.
if results_df.shape[0] > old_count:
    try:
        old_date = pd.read_sql_query("select max(updated_on) as date from new_data",conn).date[0]
    except:
        old_date = "2020-01-01"
    # Copy old data into the previous dataset
    try:
        pd.read_sql("select * from new_data",conn).to_sql("previous_data",conn,if_exists='replace')
    except:
        print("First time run?")
    
    # Format date
    results_df['updated_on'] = datetime.datetime.now().strftime("%Y-%m-%d")

    # Copy new data
    results_df.to_sql("new_data",conn,if_exists="replace")
    
    # Send the email
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    message = """
    %s
        
    There are now %s reported cases of coronavirus in Illinois in 2020, up from %s on %s.
        """ % (results_df.updated_on[0],results_df.shape[0],old_count,old_date)
    
    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email,password)
        server.sendmail(sender_email,receiver_email,message)
