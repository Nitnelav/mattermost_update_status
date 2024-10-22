import mattermost
import datetime
import os
import csv

# Load environment variables
server = os.environ.get('MATTERMOST_SERVER')
email = os.environ.get('MATTERMOST_EMAIL')
password = os.environ.get('MATTERMOST_PASSWORD')

# Load csv data
schedule = []
with open('schedule.csv', mode='r') as file:
    csv_reader = csv.DictReader(file, delimiter=';')
    schedule = [row for row in csv_reader]

# login framateam
mm = mattermost.MMApi("https://%s/api" % server)
mm.login(email, password)

user = mm.get_user()
id = user["id"]
res = None

if (user["props"]["customStatus"] == ''):
    now = datetime.datetime.now()
    current_week_day = now.strftime('%A')
    current_day = now.strftime('%Y-%m-%d')

    schedule_days = [day for day in schedule if day['day'] == current_week_day]

    if len(schedule_days) > 0:
        emoji = schedule_days[0]['emoji']
        text = schedule_days[0]['text']
        status = '{"emoji":"%s","text":"%s","duration":"today","expires_at":"%sT20:00:00.000Z"}' % (emoji, text, current_day)
        res = mm.patch_user(id, props={"props" : {'customStatus': status}})

print(res)