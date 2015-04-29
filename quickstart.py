"""A quickstart example showing usage of the Google Calendar API."""
from datetime import datetime
import os

from apiclient.discovery import build
from httplib2 import Http
import oauth2client
from oauth2client import client
from oauth2client import tools
from dateutil import tz
import pytz
from analyze import get_students
from random import randint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Calendar API Quickstart'
# calendar_id = 'cornell.edu_h7aetvgh776csueqptorr6bkjs@group.calendar.google.com'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-api-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path

    return credentials


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    service = build('calendar', 'v3', http=credentials.authorize(Http()))
    
    to_zone = tz.tzlocal()
    
    # now = datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(to_zone).isoformat() + 'Z' # 'Z' indicates UTC time
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print 'Getting the upcoming 10 events'
    # calendarResult = service.calendars().get(calendarId=calendar_id).execute()

    calendar_name = 'Bloc {}'.format(randint(0,1000000))
    calendar = {
        'summary': calendar_name,
        'timeZone': 'America/New_York'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    calendar_id = created_calendar['id']
    
    time_zone = created_calendar['timeZone']


    # print calendarResult
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    # print eventsResult5
    events = eventsResult.get('items', [])

    if not events:
        print 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print start, event['summary']

    students = get_students()
    # return students

    for student in students:
        for appt in student.appts:

            event = student.create_event(appt, time_zone)
            recurring_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print recurring_event['id']
    
    return students






# if __name__ == '__main__':
#     main()