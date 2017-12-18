"""
Destroy the database for the specified user
(who must not be siteUserAdmin)
"""
import pymongo
from pymongo import MongoClient
import sys
import config
CONFIG = config.configuration()

MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(CONFIG.DB_USER,CONFIG.DB_USER_PW,CONFIG.DB_HOST, CONFIG.DB_PORT, CONFIG.DB)
print("Using URL '{}'".format(MONGO_CLIENT_URL))

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB_HOST)
    print("Got database")
    print("Attempting drop users")
    # db.command( {"dropAllUsersFromDatabase": 1 } )
    db.remove_user(CONFIG.DB_USER)
    print("Dropped database users for {}".format(CONFIG.DB_HOST))
    db.command( {"dropDatabase": 1 } )
    print("Dropped database {}".format(CONFIG.DB_HOST))
except Exception as err:
    print("Failed")
    print(err)    
