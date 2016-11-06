from pymongo import MongoClient
import datetime
import sys, traceback


class ImageDB:
    List = None
    lastUpdateTime = None
    client = MongoClient("127.0.0.1")
    db = client.CIBR
    collection = db.ImageFeature
    orb_col = db.ORBFeature

    @staticmethod
    def getList(force_refresh=False):
        try:
            if ImageDB.lastUpdateTime is not None:
                timeDuration = (datetime.datetime.now() - ImageDB.lastUpdateTime).seconds
            tenMinutes = 30
            if ImageDB.lastUpdateTime is None or timeDuration > tenMinutes or force_refresh:
                ImageDB.List = list(ImageDB.collection.find())
                ImageDB.lastUpdateTime = datetime.datetime.now()
            return ImageDB.List
        except:
            print("*** ImageDB getList takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageDB getList takes error ***")
            raise

    @staticmethod
    def getListByLabels(labels, rlabels=[], multiObj=False):
        try:
            # dbQuery = {"$and":[{"labels.label":label,"top_n_prob":1} for label in labels]}
            dbQuery = {"labels.label1": {"$in": labels}}

            if multiObj:
                tags = [{"rlabels.tags": {"$in": rlabels}}, dbQuery]
                dbQuery = {"$or": tags}
                print dbQuery

            img_list = list(ImageDB.collection.find(dbQuery))
            return img_list
        except:
            print("*** ImageDB getListByLabels takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageDB getListByLabels takes error ***")
            raise

    @staticmethod
    def getORB(ids):
        try:
            return ImageDB.orb_col.find({"_id": {"$in": ids}})
        except:
            print("*** ImageDB getORB takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageDB getORB takes error ***")
            raise



    @staticmethod
    def getItem(param, force_refresh=False):
        item = ImageDB.collection.find_one(param)
        orb_item = ImageDB.orb_col.find_one(param)
        if item is not None and orb_item is not None:
            item["ORB"] = orb_item["ORB"]
        return item

    @staticmethod
    def insert(md5, features, path=None, url=None):
        try:
            imgObj = {}
            imgObj["ImageName"] = path[path.rfind("/") + 1:]
            imgObj['HSVFeature'] = features
            imgObj["md5"] = md5
            imgObj["CreateTime"] = datetime.datetime.utcnow()
            imgObj["UpdateTime"] = datetime.datetime.utcnow()
            if path is None and url is None:
                raise Exception("path and url can not be None")
            if path is not None:
                imgObj["Path"] = "/" + path.replace('app/', '', 1)
            if url is not None:
                imgObj["ImageUrl"] = url
            ImageDB.collection.insert_one(imgObj)
            ImageDB.getList(True)
            del imgObj['HSVFeature']
            print("insert new img item: " + str(imgObj))
        except:
            print("*** ImageDB insert takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageDB insert takes error ***")

    @staticmethod
    def insert_one(imgItem):
        imgItem["delete"] = True
        orbfeature = imgItem["ORB"]
        del imgItem['ORB']

        # insert first
        ImageDB.collection.insert_one(imgItem)
        imgItem = ImageDB.collection.find_one({'md5': imgItem['md5']})

        # insert second
        newItem = {'_id': imgItem["_id"], 'md5': imgItem['md5'], 'ORB': orbfeature}
        ImageDB.orb_col.insert_one(newItem)

        # replace first
        del imgItem["delete"]
        ImageDB.collection.replace_one({"_id": imgItem["_id"]}, imgItem)

        imgItem['ORB'] = orbfeature
        return
