
import os
import sys, traceback

from flask import Flask, render_template, request, jsonify
 
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher

# create flask instance
app = Flask(__name__)
INDEX = os.path.join(os.path.dirname(__file__), 'index.csv')

# main route
@app.route('/')
def index():
    return render_template('index.html')
# search route
@app.route('/search', methods=['POST'])
def search():

    if request.method == "POST":
        RESULTS_ARRAY = []
        # get url
        image_url = request.form.get('img')

        try:

            # initialize the image descriptor
            cd = ColorDescriptor((8, 12, 3))

            # load the query image and describe it
            from skimage import io
            import cv2
            query = io.imread(image_url)
            query = cv2.cvtColor(query,cv2.COLOR_RGB2BGR)
            features = cd.describe(query)

            # perform the search
            # searcher = Searcher(INDEX)
            results = Searcher.search(features)

            # loop over the results, displaying the score and image name
            for (score, url) in results:
                RESULTS_ARRAY.append(
                    {"image": str(url), "score": str(score)})

            # return success
            return jsonify(results=(RESULTS_ARRAY))

        except:
            print("*** app.search() takes error ***")
            print(sys.exc_info()[0])
            traceback.print_exc()
            print("*** app.search() takes error ***")
            # return error
            return jsonify({"sorry": "Sorry, no results! Please try again."}), 500

# run!
if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True)
