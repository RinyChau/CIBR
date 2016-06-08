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
        hour = str(datetime.datetime.now().hour)
        path = os.path.join(img_dir, year, hour, file_name)
        image_file.save(path)
        return path
