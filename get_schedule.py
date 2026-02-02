import requests
from icalendar import Calendar

# 1. Download the file
url = "https://calendar.google.com/calendar/ical/e253dd67fad8392bc5118eb735c8cea2face096efd14fb8edd3cefa2daf1ec60%40group.calendar.google.com/public/basic.ics"
response = requests.get(url)

# 2. Parse it
gcal = Calendar.from_ical(response.content)
events = []

for component in gcal.walk():
    if component.name == "VEVENT":
        events.append({
            'summary': str(component.get('summary')),
            'start': component.get('dtstart').dt,
            'description': str(component.get('description'))
        })

# Now you have a list of dicts with every event, time, and sport!
import pandas as pd
df = pd.DataFrame(events)
print(df.head())