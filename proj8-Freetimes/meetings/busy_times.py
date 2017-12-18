import arrow # Replacement for datetime, based on moment.js
import general_time_helpers

def find_times_busy(service, begin_datetime, end_datetime, calendars=['primary']):

    busy_times = []

    for calendar in calendars:
        events = service.events().list(calendarId=calendar, singleEvents=True, orderBy="startTime", timeMin=begin_datetime, timeMax=end_datetime).execute()['items']

        for event in events:
            if event.get('transparency') != "transparent":
               busy_times.append({'start': event['start']['dateTime'], 'end': event['end']['dateTime'], 'summary': event['summary']})
    return busy_times