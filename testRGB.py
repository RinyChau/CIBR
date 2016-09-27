from skimage import io
from PIL import Image

url = "http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/dataset/110001.png"
query = io.imread(url)
print(query)
