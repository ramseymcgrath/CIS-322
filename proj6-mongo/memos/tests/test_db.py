import arrow
import nose  # Testing framework
from pymongo import MongoClient
import config
import logging

CONFIG = config.configuration()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
log = logging.getLogger(__name__)

MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(CONFIG.DB_USER,CONFIG.DB_USER_PW,CONFIG.DB_HOST,CONFIG.DB_PORT,CONFIG.DB)

try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)


def test_addition():
    counter = collection.count()
    collection.insert_one({"type": "test_memo", "token": 1})
    assert collection.count() == counter + 1
def test_addition2():
    counter = collection.count()
    collection.insert_one({"type": "test_memo", "token": 2})
    assert collection.count() == counter + 2

def test_del():  
    counter = collection.count()
    collection.delete_one({"token": 2})
    assert collection.count() == counter - 1
def test_del2():
    counter = collection.count()
    collection.delete_one({"token": 1})
    assert collection.count() == counter - 2