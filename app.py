import os
import sys
import traceback

from flask import Flask, render_template, request, jsonify
from dao.imagedb import ImageDB

from pyimagesearch.searcher import Searcher
from pyimagestore.imgManagement import ImgManagement
from pyimagesearch.searcher import DistanceType
from pyimagesearch.colordescriptor import Feature
import urllib, cStringIO, thread
from random import randint

# create flask instance
app = Flask(__name__)

img_dir = os.path.join(os.path.dirname(__file__), 'static', 'image', "upload")
img_url_dir = os.path.join(os.path.dirname(__file__), 'static', 'image', "url")

# initialize the image descriptor
feature_type = Feature.LUV
distance_type = DistanceType.L1

top_n_classes = 5
# initialize the searcher
searcher = Searcher(DistanceType.L1, feature_type, top_n_classes)


# main route
@app.route('/')
def index():
    return render_template('index.html')

# search route
@app.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        result_array = []
        # get url
        image_url = request.form.get('url')
        image_file = request.files['img'] if 'img' in request.files else None
        try:
            # load the query image and describe it
            if image_file is not None and image_file.filename != '':
                results = searchImgByFile(image_file)
            elif image_url.startswith("/"):
                results = searchImgByLocalFile(image_url)
            else:
                results = searchImgByUrl(image_url)

            data = results["data"]
            data_array = []
            for result in data:
                data_array.append(
                    {"path": str(result["path"]), "distance": result["distance"], "labels": result["labels"]})
            # loop over the results, displaying the score and image name
            # for (score, url) in results:
            #     result_array.append(
            #         {"image": str(url), "score": str(score)})


            # return success
            return jsonify(data=data_array,labels=results["labels"])
        except:
            print("*** app.search() takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** app.search() takes error ***")
            # return error
            return jsonify({"sorry": "Sorry, no results! Please try again."}), 500


def searchImgByLocalFile(path):
    imagePath = "app" + path
    imgMD5 = ImgManagement.getMD5(imagePath)
    imageItem = ImageDB.getItem({"md5": imgMD5})
    return searcher.search_by_features(imageItem)

def searchImgByFile(image_file):
    imagePath = ImgManagement.saveFile(img_dir, image_file)
    imgMD5 = ImgManagement.getMD5(imagePath)
    imageItem = ImageDB.getItem({"md5": imgMD5})

    if imageItem is None:

        # image = Image.open(imagePath, 'r')
        # delete all upload file
        result = searcher.search(imagePath)
        thread.start_new_thread(ImgManagement.deleteFile, (imagePath,))
        return result

        # thread.start_new_thread(ImageDB.insert, (imgMD5, features, imagePath,))
    else:
        # delete all upload file
        thread.start_new_thread(ImgManagement.deleteFile, (imagePath,))
        return searcher.search_by_features(imageItem)
        # thread.start_new_thread(ImgManagement.deleteFile, (imagePath,))


def searchImgByUrl(image_url):
    file = urllib.URLopener()
    directory = ImgManagement.getTimeDir(img_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, str(randint(0, 100000000)))
    while os.path.isfile(path):
        path = os.path.join(directory, str(randint(0, 100000000)))

    file.retrieve(image_url, path)
    return searcher.search(path)

    # results = searcher.search(features)
    # thread.start_new_thread(ImgManagement.saveUrl, (image_url, img_url_dir,))
    # return results
    # pass

# run!
if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
