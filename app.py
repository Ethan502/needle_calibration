from flask import Flask, redirect, url_for, render_template, request
import os
import cv2 as cv

from finder_class import CalibrationPoints


app = Flask(__name__)

image_folder = os.path.join('static', 'images')
processed_folder = os.path.join('static', 'processed')

app.config["IMAGE_FOLDER"] = image_folder
app.config["PROCESSED_FOLDER"] = processed_folder


@app.route("/", methods=['POST', 'GET'])
def home():

    filelist = os.listdir(image_folder)

    if request.method == 'POST':
        original_image = os.path.join(app.config["IMAGE_FOLDER"], request.form["file1"])
        img_data = cv.imread(original_image)

        points = CalibrationPoints(img_data)
        points.process()
        new_data = points.img

        cv.imwrite(os.path.join(app.config["PROCESSED_FOLDER"], 'processed.jpg'), new_data)
        new_pic = (os.path.join(app.config["PROCESSED_FOLDER"], 'processed.jpg'))
        
        return render_template("index.html", filelist=filelist, 
                                len = len(filelist), final_og_pic=original_image,
                                final_new_pic = new_pic)                           
    else:
        return render_template("index.html", filelist = filelist, len = len(filelist))

if __name__ == "__main__":
    app.run(debug=True)