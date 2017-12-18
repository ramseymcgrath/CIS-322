"""
Mapping application
"""
import uuid
import logging
import json
import flask
from flask import request, g
import pre  # Location parsing code lives here
import config

###
# Globals
###
map_application = flask.Flask(__name__)
CONFIG = config.configuration()
map_application.secret_key = CONFIG.SECRET_KEY

###
# Pages
###

@map_application.route("/")
@map_application.route("/index")
def index():
    map_application.logger.debug("Main page entry")
    return flask.render_template('index.html')

@map_application.route('/_capitols')
def capitols():
    map_application.logger.debug("Capitols call entry")
    found_capitols = pre.process("poi.xml",True)
    return flask.jsonify(result=found_capitols)

@map_application.errorhandler(404)#Bad User
def page_not_found(error):
    map_application.logger.debug("Page not found")
    map_application.logger.debug(error)
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html')

######

map_application.debug = CONFIG.DEBUG
if map_application.debug:
    map_application.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    map_application.secret_key = str(uuid.uuid4())
    map_application.debug=CONFIG.DEBUG
    map_application.logger.setLevel(logging.DEBUG)
    print("Opening for global access on port {}".format(CONFIG.PORT))
    map_application.run(port=CONFIG.PORT, host="0.0.0.0")
    