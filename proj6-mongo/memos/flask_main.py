"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""
import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for
import json
import logging
import os
import sys
import binascii
from uuid import uuid4
import arrow   
from dateutil import tz  # For interpreting local times
from pymongo import MongoClient # Mongo database
import config
CONFIG = config.configuration()
rand_token = uuid4()

MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(CONFIG.DB_USER,CONFIG.DB_USER_PW,CONFIG.DB_HOST, CONFIG.DB_PORT, CONFIG.DB)
print("Using URL '{}'".format(MONGO_CLIENT_URL))


###
# Globals
###

app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY

####
# Database connection per server process
###

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)
###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Main page entry")
  g.memos = get_memos()
  for memo in g.memos: 
      app.logger.debug("Memo: " + str(memo))
  return flask.render_template('index.html')


# We don't have an interface for creating memos yet
@app.route("/create")
def create():
    app.logger.debug("Create")
    return flask.render_template('create.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html', badurl=request.base_url, linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human

@app.route("/add_memo")
def add_memo():
    """
    Generate unique token, and add memo to DB
    """
    app.logger.debug("Got a Memo")
    token = binascii.hexlify(os.urandom(10)).decode()
    memo_date = request.args.get('date')
    memo_text = request.args.get("memo_text")

    myMemo ={"type": "dated_memo", "date": str(arrow.get(memo_date)), "text": memo_text, "token": token}
    try:
        result = myMemo
        collection.insert_one(myMemo)
        del result['_id']
        app.logger.debug("added a Memo")
    except:
        app.logger.debug("Could not add Memo")
        result = False

    return flask.jsonify(result=result)

@app.route("/del_memo")
def del_memo():
    """
    Delete Memo using unique token
    """
    app.logger.debug("Got a Token")
    token = request.args.get('token')

    try:
        collection.delete_one({"token": token})
        app.logger.debug("removed a memo")
        result = True
    except:
        app.logger.debug("could not remove memo")
        result = False

    return flask.jsonify(result=result)

#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ):
        record['date'] = arrow.get(record['date']).isoformat()
        del record['_id']
        records.append(record)
    return records 


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")