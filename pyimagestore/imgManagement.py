import os
import sys, traceback
import datetime
from werkzeug.utils import secure_filename

from dao.imagedb import ImageDB
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher
import urllib
from random import randint
import hashlib
import cv2
import urllib, cStringIO
from PIL import Image

detect_dir = os.path.join(os.path.dirname(__file__), 'static', 'image', "tmp")
class ImgManagement:

    @staticmethod
    def saveFile(img_dir, image_file):
        file_name = secure_filename(image_file.filename)
        directory = ImgManagement.getTimeDir(img_dir)
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, file_name)
        while (os.path.isfile(path)):
            if file_name.rfind('.') >= 0:
                newFileName = file_name[0:file_name.rfind('.')] + str(randint(0, 1000)) + \
                              file_name[file_name.rfind('.'):]
            else:
                newFileName = file_name + str(randint(0, 1000))
            path = os.path.join(directory, newFileName)
        image_file.save(path)
        print("save file" + path)
        return path

    @staticmethod
    def getMD5(path):
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def deleteFile(path):
        os.remove(path)
        print("remove duplicate file : " + path)

    @staticmethod
    def saveUrl(url, img_dir):
        try:
            file = urllib.URLopener()
            directory = ImgManagement.getTimeDir(img_dir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            path = os.path.join(directory, str(randint(0, 100000000)))
            while os.path.isfile(path):
                path = os.path.join(directory, str(randint(0, 100000000)))

            file.retrieve(url, path)
            md5 = ImgManagement.getMD5(path)
            if ImageDB.getItem({"md5": md5}) is not None:
                ImgManagement.deleteFile(path)
            else:
                image = Image.open(path)
                cd = ColorDescriptor((8, 12, 3))
                features = cd.describe(image)
                ImageDB.insert(md5, features, path)
                ImageDB.getList(True)
        except:
            print("*** ImageManagement saveUrl takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** ImageManagement saveUrl takes error ***")

    @staticmethod
    def getTimeDir(base_dir):
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().month)
        day = str(datetime.datetime.now().day)
        directory = os.path.join(base_dir, year, month, day)
        return directory

    @staticmethod
    def saveDetectImage(path,obj_list):
        dir = ImgManagement.getTimeDir(detect_dir)
        name = path[path.rfind("/") + 1:]
        full_path = os.path.join(dir,name)
        im = cv2.imread(path)
        pass

