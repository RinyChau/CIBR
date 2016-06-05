import pymongo
from pymongo import MongoClient
import datetime
import sys, traceback
class ImageDB:
    def __init__(self):
        self.List = None
        self.lastUpdateTime = None

    def getList(self,force_refresh=False):
        try:
            if self.lastUpdateTime is not None:
                timeDuration = (datetime.datetime.now() - self.lastUpdateTime).seconds
            tenMinutes = 600
            if self.lastUpdateTime is None or timeDuration > tenMinutes or force_refresh:
                client = MongoClient()
                db = client.CIBR
                collection = db.ImageFeature
                self.List = collection.find()
                self.lastUpdateTime = datetime.datetime.now()
            return self.List
        except:
            print("*** ImageDB getList takes error ***")
            print(sys.exc_info()[0])
            traceback.print_stack()
            print("*** ImageDB getList takes error ***")
