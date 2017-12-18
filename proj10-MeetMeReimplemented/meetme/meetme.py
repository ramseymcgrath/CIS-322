# -*- coding: utf-8 -*-
import os
import flask
from flask import Flask, redirect, url_for, session, render_template, request, flash, _app_ctx_stack 
from oauth2client import client
from sqlite3 import dbapi2 as sqlite3
from flask import g
import httplib2
import googleapiclient
from googleapiclient import discovery
import arrow
from dateutil import tz
import config

#Globals
CLIENT_SECRET_FILE  = "client_secret.json"
DATABASE            = './db/test.db'
SCOPES              = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.readonly']
API_SERVICE_NAME    = 'MeetMe'
API_VERSION         = 'v2'

app = flask.Flask(__name__)
app.secret_key = str(os.urandom(24))

#########################
#
#Routing
#
#########################

#Base Routes
@app.route("/")
@app.route("/index")
def index():
    if 'begin_date' not in flask.session:
        init_session_values()
    return flask.redirect(flask.url_for('timeline'))

#handles showing a list of a users friends
@app.route('/list_friends',methods=['GET','POST'])
def list_friends():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))
    if request.method == 'GET':
        friends = get_friends(credentials['user_id'])
        return render_template("friends.html", friends=friends)                 

#shows upcoming meetings in a nice timeline view
@app.route('/timeline')
def timeline():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))
    flask.g.user = get_user_profile()
    events = get_upcoming_events('primary', 10)
    if not events:
        return render_template("timeline.html", events=[])
    return render_template("timeline.html", events=events)

#start of making a new event, add event info, and select an open time
@app.route('/make_new_meeting',methods=['GET','POST'])
def make_new_meeting():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))   
    
    if request.method == 'GET':
        free_times = get_free_times('primary',request.form['start_datetime'],
                                    request.form['stop_datetime'])
        return render_template("new_event_time.html", freetimes=free_times)
    
    if request.method == 'POST':
        result = request.form.todict()
        try:
            #hit google and try to add evennt to calendar
            meeting_time = result.get('meeting_time').split(',')
            starttime = meeting_time[0]
            endtime = meeting_time[1]
            event = {
                'summary': result.get('event_title', "Default Summary"),
                'location': result.get('event_location', "Default Location"),
                'description': result.get('event_description', "Default Description"),
                'start': {
                    'dateTime': starttime,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': endtime,
                    'timeZone': 'America/Los_Angeles',
                }
            }

            event_id = create_event('primary', event)
            flash('New event created in your calendar')
            #add this event to the DB
            try:
                add_new_meeting(event_id,credentials['client_id'])
            except:
                flash('DB Error')
            #move client on to the invite stage
            return flask.redirect("new_event_users")
        except:
            flash('We encountered a problem with your event, please try again')
            return flask.redirect("timeline")

#choose users you'd like to invite
@app.route('/new_event_users',methods=['GET','POST'])
def make_invite():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))
    
    if request.method == 'GET':
        friends = []
        try:
            friends = get_friends(session['credentials']['client_id'])
        except:
            flash('We encountered a problem with your friends query, please try again')
        return render_template("new_event_user.html", friends=friends)
    
    if request.method == 'POST':
        try:
            if request.values["invites"]:
                usersToInvite = request.values["invites"]
                for user in usersToInvite:
                    add_attendee('primary', session['new_event_id'], user)
                flash('Invites sent successfully')
            else:
                flash('Personal event, no invites sent')
            return flask.redirect("/")
        except:
            return flask.redirect("timeline")        

@app.route('/register',methods=['GET','POST'])
def register():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))   

    if request.method == 'GET':
        return render_template(register.html)
    if request.method == 'POST':
        username = request.data.get('username')
        gmail = getEmail()
        profile = get_user_profile()
        try:
            gmail = getEmail()
            add_new_user(username,profile['emailAddress'])
            flash('Success!')  
        except:
            flash('Failed!')
    return flask.redirect("timeline")

@app.route('/logout')
def logout():
    credentials = valid_credentials()
    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())

#########################
#
#AUTH CODE
#
#########################

def valid_credentials():
    if 'credentials' not in flask.session:
        return None
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if (credentials.invalid or credentials.access_token_expired):
        return None
    return credentials

@app.route('/oauth2callback')
def oauth2callback():
    flow =  client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope= SCOPES,
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return(flask.redirect('timeline'))


#########################
#
#Initialization
#
#########################

def initialize_gmail(credentials):   
    http_auth = credentials.authorize(httplib2.Http())
    gmail = discovery.build('gmail', 'v1', http=http_auth)
    return gmail

def getEmail():
    appContext = _app_ctx_stack.top
    gmail = getattr(appContext, "gmail", None)
    if gmail is None:
        credentials = valid_credentials()
        gmail = initialize_gmail(credentials)
        appContext.gmail = gmail
    return gmail

def initialize_service(credentials):   
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http_auth)
    return service

def getService():
    appContext = _app_ctx_stack.top
    service = getattr(appContext, "service", None)
    if service is None:
        credentials = valid_credentials()
        service = initialize_service(credentials)
        appContext.service = service
    return service

def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main. 
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')     # We really should be using tz from browser
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))

################################
#   
#Calendar functions
#
###############################

def get_user_profile():
    gmail = getEmail()
    profile = gmail.users().getProfile(userId='me').execute()
    return profile
    
def get_upcoming_events(usercalendarId, numberOfEvents):
    now = arrow.now('local').isoformat()
    service = getService()
    page_token = None
    result =[]
    while True:
        events = service.events().list(calendarId='primary', pageToken=page_token).execute()
        result.append(events['items'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return result

def get_free_times(usercalendarId, time_min, time_max):
    result = get_busy_times(usercalendarId, time_min, time_max)
    pendulumArray = busyArray(result)
    return find_free_times(time_min,time_max,pendulumArray)

def create_event(usercalendarId, event):
    service = getService()
    # Create an event and add it to the calendar
    event = service.events().insert(usercalendarId, sendNotifications=True, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event.get('eventId')

#Friend code
def allow_freebusy_to_user(userToAllowEmail, usercalendarId='primary'):
    service = getService()
    rule = {
        'scope': {
            'type': 'user',
            'value': userToAllowEmail
    },
    'role': 'freeBusyReader'
    }
    created_rule = service.acl().insert(calendarId=usercalendarId, body=rule).execute()
    print(created_rule['id'])

def add_attendee(usercalendarId, event_id, attendeeEmail):
    service = getService()
    event = service.events().get(calendarId=usercalendarId, eventId=event_id, sendNotifications=True).execute()
    attendees = event.get('attendees', [])
    attendees.append({'email':attendeeEmail})
    updated_event = service.events().update(calendarId=usercalendarId, eventId=event[event_id], body=event).execute()

def get_attendee_status(usercalendarId, event_id):
    service = getService()
    event = service.events().get(calendarId=usercalendarId, eventId=event_id).execute()
    attendees = event.get('attendees', [])

def get_user_email(user_id):
    service = getService()
    results = service.users().labels().list(user_id='me').execute()
    labels = results.get('labels', [])
    if not labels:
        return
    else:
        return labels[0]

def get_calendar_list():
    service = getService()
    calendar_list_entry = service.calendarList().get(calendarId='primary').execute()
    return calendar_list_entry['summary']   

def get_busy_times(usercalendarId, time_min, time_max):
    service = getService()
    # Construct freebusy query request's body
    freebusy_query = {
        "timeMin" : time_min,
        "timeMax" : time_max,
        "items" :[
            {
                "id" : usercalendarId
            }
        ]
    }
    result = service.freebusy().query(body=freebusy_query).execute()
    return result

def busyArray(jsonresult):
    busyArray = jsonresult["calendars"]["primary"]["busy"]
    pendulumArray = []
    for item in busyArray:
        start = pendulum.parse(item['start'])
        end = pendulum.parse(item['end'])
        period = pendulum.period(start, end)
        pendulumArray = pendulumArray + period
    return pendulumArray

def find_free_times(time_min, time_max, pandulumArray):
    wholePeriod = pendulum.period(time_min,time_max)
    busy = wholePeriod.intersect(pandulumArray)
    freeTime = wholePeriod - busy
    return freeTime


################################
#
#Database functions
#
###############################

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
    	db = g._database = sqlite3.connect(DATABASE)
    	db.row_factory = sqlite3.Row
    return db
  
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def exec_db(query, args=(), one=False):
    db = get_db()
    db.execute(query)
    res = db.commit()
    return res

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#Missing some variables, these will probably error out until we can save them somewhere
def new_friend_request(user_id, friend_id):
    exec_db('insert into friends (user_id, friend_id, friend_status) values (?, ?)',[user_id, friend_id, 'requested'])
    return

def get_friends(user_id):
    friend_ids = query_db("select friend_id from friends where user_id = '%s'" %(user_id))
    return friend_ids

def get_friends_email(user_id):
    email = query_db("select email from users where user_id = '%s'" %(user_id))
    return email

def add_new_meeting(meeting_id, host_id):
    exec_db('insert into meetings (meeting_id, host_id) values (?, ?)',[meeting_id, host_id])
    return

def add_new_user(user_id,user_email):
    query_db('insert into users (user_id, user_email) values (?, ?)',[user_id, user_email])
    return  

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: 
        db.close()

if __name__ == '__main__':
    CONFIG = config.configuration()
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # Flask on localhost doesn't actually need a cert for ssl
    port = 8080
    if CONFIG.PORT:
        port = CONFIG.PORT
    app.run('localhost', port, debug=True, ssl_context='adhoc')
