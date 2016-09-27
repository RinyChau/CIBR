import os
import sys
sys.path.append("app/dist/sklearn_theano-0.0.1-py2.7.egg")
import traceback

from flask import Flask, render_template, request, jsonify
from dao.imagedb import ImageDB
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher
from pyimagesearch.CNNClassifier import CNNClassifier
from pyimagestore.imgManagement import ImgManagement
from skimage import io
from pyimagesearch.searcher import DistanceType
from pyimagesearch.colordescriptor import Feature
import cv2
import thread
import numpy as np

from PIL import Image
# create flask instance
app = Flask(__name__)

img_dir = os.path.join(os.path.dirname(__file__), 'static', 'image', "upload")
img_url_dir = os.path.join(os.path.dirname(__file__), 'static', 'image', "url")

# initialize the image descriptor
feature = Feature.LUV
distance_type = DistanceType.L1
cd = ColorDescriptor(feature=feature)
# initialize the searcher
searcher = Searcher(DistanceType.L1, feature)

# initialize CNNClassifier
top_n_classes = 2
top_n_array = [x for x in range(1, top_n_classes + 1)]

classifier = CNNClassifier(top_n_classes)
label = "labels"

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
            else:
                results = searchImgByUrl(image_url)

            result_array = []
            for result in results:
                result_array.append(
                    {"path": str(result["path"]), "distance": result["distance"], "labels": result["labels"]})
            # loop over the results, displaying the score and image name
            # for (score, url) in results:
            #     result_array.append(
            #         {"image": str(url), "score": str(score)})


            # return success
            return jsonify(results=(result_array))
        except:
            print("*** app.search() takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** app.search() takes error ***")
            # return error
            return jsonify({"sorry": "Sorry, no results! Please try again."}), 500


def searchImgByFile(image_file):
    imagePath = ImgManagement.saveFile(img_dir, image_file)
    imgMD5 = ImgManagement.getMD5(imagePath)
    imageItem = ImageDB.getItem({"md5": imgMD5})

    if imageItem is None:
        image = np.array(Image.open(imagePath, 'r'))
        features = cd.describe(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        labels = parse_label(classifier.predict(image))

        # image = cv2.imread(imagePath)
        # features = cd.describe(image)
        # results = searcher.search(features)

        # thread.start_new_thread(ImageDB.insert, (imgMD5, features, imagePath,))
    else:
        features = imageItem[feature]
        # top_n_array = [x for x in range(1, top_n_classes+1)]
        labels = [x["label"] for x in imageItem["labels"] if x["top_n_prob"] in top_n_array]
        # results = searcher.search(features)
        # thread.start_new_thread(ImgManagement.deleteFile, (imagePath,))

    # delete all upload file
    thread.start_new_thread(ImgManagement.deleteFile, (imagePath,))

    return searchImg(features, labels)
    # return results


def parse_label(labels):
    label_list = []
    # top_n_prob = 0
    for tags in labels.ravel():
        # top_n_prob += 1
        for tag in tags.split(","):
            label_list.append(tag)
            # label.append({"label": tag, "top_n_prob": top_n_prob})
    return label_list


def searchImgByUrl(image_url):
    query = io.imread(image_url)
    labels = parse_label(classifier.predict(query))
    features = cd.describe(cv2.cvtColor(query, cv2.COLOR_RGB2BGR))
    # results = searcher.search(features)

    # thread.start_new_thread(ImgManagement.saveUrl, (image_url, img_url_dir,))
    return searchImg(features, labels)
    # return results


def searchImg(features, labels):
    return searcher.search_by_labels(queryFeatures=features, labels=labels)
    # pass

# run!
if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True)
