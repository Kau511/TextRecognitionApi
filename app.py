from flask import Flask, request, jsonify
import cv2, urllib, urllib.request
import pytesseract
from PIL import Image
import os
import numpy as np
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
# from config import config
import pyrebase
import re
import datetime



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# firebase = pyrebase.initialize_app(config)
# storage = firebase.storage()

app = Flask(__name__)
CORS(app)


# def deskew(image):
#     coords = np.column_stack(np.where(image > 0))
#     angle = cv2.minAreaRect(coords)
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#     return rotated

def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET','POST'])
def check_image():
    if 'image' not in request.files:
        return ("Upload image to get text")
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename1 = secure_filename(file.filename)
            print(filename1)
            file.save(filename1)
            # storage.child("textrecog/" +str(filename)).put(file)
            # link1 = storage.child("textrecog/" + str(filename)).get_url(None)
    # resp = urllib.request.urlopen(link1)
    # image = np.asarray(bytearray(resp.read()), dtype="uint8")
    # image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image = cv2.imread(filename1,cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = opening(gray)
    # cv2.imshow("skewed",image)
    # cv2.waitKey(0)
    _, threshold_img = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    filename2 = "{}.png".format(os.getpid())
    cv2.imwrite(filename2, gray)
    # cv2.imwrite(filename2, threshold_img)
    # cv2.imshow("th",gray)
    # cv2.waitKey(0)
    config = ('-l eng+hin --oem 3 --psm 6')
    text = pytesseract.image_to_string(Image.open(filename2),config = config)
    out = dict()
    lines = text
    lines_splitted = lines.split('\n')
    block = "".join([s for s in text.strip().splitlines(True) if s.strip("\r\n").strip()])
    print(block)
    words = ' '.join(lines_splitted).split()
    res = [x.strip() for x in lines_splitted if x.strip()]
    out['lines'] = res
    out['Words'] = words
    out['full text'] = block
    os.remove(filename1)
    os.remove(filename2)
    return jsonify(out)

if __name__ == "__main__":
    app.run(debug=True)


