"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations put into a seperate file
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY


###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)#Bad User
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#   Took out the fix me and added the actual fixes, and broke it into more sane methods
#
###############
@app.route("/_calc_times")
def calc_times():
    """
    Calculates open/close times from miles, using rules 
    described at http://www.rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles. 
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    #Broke this parsing into a seperate method
    open_time, b_distance, begintime = calcVariables(km)
    #Avoid no open time error
    if not open_time:
        return flask.jsonify(result=False)
    #Broke time calculation out into its own method
    return timeCalculation(km, b_distance, begintime, open_time)

#takes in the calculated variables above, gives us the json
def timeCalculation(km, b_distance, begintime, open_time):
    close_time = acp_times.close_time(km, b_distance, begintime)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

#Take in our time zone, brev distance etc and return the calculated value
def calcVariables(km):
    #Get timezone and dist
    timezone = request.args.get('tz', type=str) 
    b_distance = request.args.get('brev_dist', type=int)

    #Format the variables, use acp_times and then send em back
    begintime = arrow.get(request.args.get('bd', type=str) + " " + request.args.get('bt', type=str), 'YYYY-MM-DD HH:mm').replace(tzinfo=timezone).isoformat()
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(km, b_distance, begintime)
    return open_time, b_distance, begintime


######

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    import uuid #this should be at the top, but eh
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
