import flask
from flask import render_template
from flask import request
from flask import url_for
import uuid
import json
import logging
# Date handling 
import arrow # Replacement for datetime, based on moment.js
from dateutil import tz
# OAuth2  - Google library implementation for convenience
from oauth2client import client

###
# Globals
###
import config
import busy_times
import free_times
import general_time_helpers
import service_helpers

if __name__ == "__main__":
    CONFIG = config.configuration()
else:
    CONFIG = config.configuration(proxied=True)

app = flask.Flask(__name__)
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key=CONFIG.SECRET_KEY

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = CONFIG.GOOGLE_KEY_FILE  ## You'll need this
APPLICATION_NAME = 'MeetMe class project'

#############################
#
#  Pages (routed from URLs)
#
#############################

@app.route("/")
@app.route("/index")
def index():
    if 'begin_date' not in flask.session:
        init_session_values()
    return render_template('index.html')

@app.route("/choose")
def choose():
    ## We'll need authorization to list calendars 
    ## I wanted to put what follows into a function, but had
    ## to pull it back here because the redirect has to be a
    ## 'return' 
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials(flask)
    if not credentials:
        app.logger.debug("Redirecting to authorization")
        return flask.redirect(flask.url_for('oauth2callback'))
    

    if 'daterange' not in flask.session:
        init_session_values()
        return render_template('index.html') 
    
    gcal_service = service_helpers.get_gcal_service(credentials)

    flask.g.calendars = service_helpers.list_calendars(gcal_service)
    flask.g.desired_blocks = free_times.find_free_times(gcal_service, flask.g.calendars, flask.session['daterange'])
    return render_template('index.html')

def valid_credentials(flask):
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value. 
    """
    if 'credentials' not in flask.session:
        return None

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if (credentials.invalid or
        credentials.access_token_expired):
        return None
    return credentials

@app.route('/oauth2callback')
def oauth2callback():
  """
  The 'flow' has this one place to call back to.  We'll enter here
  more than once as steps in the flow are completed, and need to keep
  track of how far we've gotten. The first time we'll do the first
  step, the second time we'll skip the first step and do the second,
  and so on.
  """
  app.logger.debug("Entering oauth2callback")
  flow =  client.flow_from_clientsecrets(
      CLIENT_SECRET_FILE,
      scope= SCOPES,
      redirect_uri=flask.url_for('oauth2callback', _external=True))

  if 'code' not in flask.request.args:   
    app.logger.debug("Code not in flask.request.args")
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('choose'))

#####
#
#  Option setting:  Buttons or forms
#
#####

@app.route('/setrange', methods=['POST'])
def setrange():
    """
    User chose a date range with the bootstrap daterange
    widget.
    """

    daterange = request.form.get('daterange')
    if daterange:
        flask.session['daterange'] = daterange
        app.logger.debug("setting daterange")
    else:
       flask.flash("Setrange gave us no data") 
    return flask.redirect(flask.url_for('choose'))

####
#
#   Initialize session variables 
#
####
def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main. 
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 8 to 5
    flask.session["begin_time"] = general_time_helpers.interpret_time("9am")
    flask.session["end_time"] = general_time_helpers.interpret_time("5pm")
  

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( time )
        return normal.format("HH:mm")
    except:
        return "(bad time)"
    
#############

if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    app.secret_key = str(uuid.uuid4())  
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)

    if CONFIG.DEBUG:
        app.run(port=CONFIG.PORT)
    else:
        # Reachable from anywhere 
        app.run(port=CONFIG.PORT,host="0.0.0.0")
