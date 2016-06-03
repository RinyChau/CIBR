import pymongo
from pymongo import MongoClient
import datetime
class ImageDB:
    def __init__(self):
        self.List = None
        self.lastUpdateTime = None

    def getList(self,force_refresh=False):
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

