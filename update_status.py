import mattermost
from datetime import datetime as dt, UTC
import json
import os
import csv

# Load environment variables
server = os.environ.get('MATTERMOST_SERVER')
email = os.environ.get('MATTERMOST_EMAIL')
password = os.environ.get('MATTERMOST_PASSWORD')

if server is None:
    print("MATTERMOST_SERVER environment variable is not set. Exiting.")
    exit()

if email is None:
    print("MATTERMOST_EMAIL environment variable is not set. Exiting.")
    exit()

if password is None:
    print("MATTERMOST_PASSWORD environment variable is not set. Exiting.")
    exit()

# Load csv data
schedule = []
try:
    with open('schedule.csv', mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        schedule = [row for row in csv_reader]
except FileNotFoundError:
    print("File schedule.csv not found. Exiting.")
    exit()
except Exception as e:
    print("Error reading schedule.csv: %s" % e)
    exit()

# login framateam
mm = mattermost.MMApi("https://%s/api" % server)
login_res = mm.login(email, password)

if login_res is None:
    print("Login failed. Exiting.")
    exit()

user = mm.get_user()
id = user["id"]
res = None

now = dt.now(UTC)

if (user["props"]["customStatus"] != ''):
    expireDate = dt.fromisoformat(json.loads(user["props"]["customStatus"])["expires_at"])
    if now < expireDate:
        print("Custom status already set. Do nothing.")
        exit()

current_week_day = now.strftime('%A')
current_day = now.strftime('%Y-%m-%d')

schedule_days = [day for day in schedule if day['day'] == current_week_day]

if len(schedule_days) < 0:
    print("No schedule for today. Do nothing.")
    exit()

emoji = schedule_days[0]['emoji']
text = schedule_days[0]['text']
status = '{"emoji":"%s","text":"%s","duration":"today","expires_at":"%sT20:00:00.000Z"}' % (emoji, text, current_day)
res = mm.patch_user(id, props={"props" : {'customStatus': status}})

print("Status Updated: %s" % status)