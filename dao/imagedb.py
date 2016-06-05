from pymongo import MongoClient
import datetime
import sys, traceback


class ImageDB:
    List = None
    lastUpdateTime = None

    @staticmethod
    def getList(force_refresh=False):
        try:
            if ImageDB.lastUpdateTime is not None:
                timeDuration = (datetime.datetime.now() - ImageDB.lastUpdateTime).seconds
            tenMinutes = 600
            if ImageDB.lastUpdateTime is None or timeDuration > tenMinutes or force_refresh:
                client = MongoClient()
                db = client.CIBR
                collection = db.ImageFeature
                ImageDB.List = list(collection.find())
                ImageDB.lastUpdateTime = datetime.datetime.now()
            return ImageDB.Licst
        except:
            print("*** ImageDB getList takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageDB getList takes error ***")
            raise
