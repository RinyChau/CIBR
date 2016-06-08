import os
import sys, traceback
import datetime
from werkzeug.utils import secure_filename
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher


class ImgManagement:
    @staticmethod
    def saveFile(img_dir, image_file):
        file_name = secure_filename(image_file.filename)
        year = str(datetime.datetime.now().year)
        month = str(datetime.datetime.now().month)
        day = str(datetime.datetime.now().day)
        hour = str(datetime.datetime.now().hour)
        dir = os.path.join(img_dir, year, month, day, hour)
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = os.path.join(dir, file_name)
        image_file.save(path)
        return path
