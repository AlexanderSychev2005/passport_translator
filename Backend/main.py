from flask import Flask, request
from flask import render_template
import settings
import utils
import numpy as np
import cv2
import passport_results # Assuming this is a custom module for passport results
import document_results # Assuming this is a custom module for document results

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

docscan = utils.DocumentScan()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/scan', methods=['GET', 'POST'])
def scandoc():
    if request.method == 'POST':
        file = request.files['image_name']
        upload_image_path = utils.save_upload_image(file)
        print('Img save in =', upload_image_path)
        # predict the coordianates
        four_points, size = docscan.document_scanner(upload_image_path)
        print(four_points, size)
        if four_points is None:
            message = 'UNABLE TO LOCATE THE CORDANATES'
            points = [
                {'x': 0, 'y': 10999999},
                {'x': 0, 'y': 0},
                {'x': 0, 'y': 0},
                {'x': 0, 'y': 0}
            ]
            return render_template('scaner.html', points=points, fileupload=True,
                                   message=message)
        else:
            points = utils.array_to_json_format(four_points)
            message = 'Located the Cordinets of Document  '
            return render_template('scaner.html', points=points, fileupload=True, message=message)

    return render_template("scaner.html")

@app.route('/scandoc', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        file = request.files['image_name']
        upload_image_path = utils.save_upload_image(file)
        print('Img save in =', upload_image_path)
        # predict the coordianates
        four_points, size = docscan.document_scanner(upload_image_path)
        print(four_points, size)
        if four_points is None:
            message = 'UNABLE TO LOCATE THE CORDANATES'
            points = [
                {'x':0 , 'y': 0},
                {'x': 420, 'y':0},
                {'x': 0, 'y': 420},
                {'x': 420, 'y': 420}
            ]
            return render_template('scanerdoc.html', points=points, fileupload=True,
                                   message=message)
        else:
            points = utils.array_to_json_format(four_points)
            message = 'Located the Cordinets of Document  '
            return render_template('scanerdoc.html', points=points, fileupload=True, message=message)

    return render_template("scanerdoc.html")

@app.route('/transform', methods=['POST'])
def transform():
    try:
        points = request.json['data']
        array = np.array(points)
        magic_color = docscan.calibrate_to_original_size(array)
        # utils.save_image(magic_color,'magic_color.jpg')
        filename = 'magic_color.jpg'
        magic_image_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(magic_image_path, magic_color)

        return "success"
    except:
        return "fail"


@app.route('/prediction')
def prediction():
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, 'magic_color.jpg')
    results = passport_results.getData(wrap_image_filepath)
    return render_template("prediction.html", results=results)


@app.route('/file_translation')
def file_translation():
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, 'magic_color.jpg')
    translated_text, html_with_entities_name = document_results.getData(wrap_image_filepath)
    html_filepath = settings.join_path(settings.MEDIA_DIR, html_with_entities_name)
    with open(html_filepath, 'r', encoding='utf-8') as f:
        html_with_entities = f.read()
    return render_template("file_translation.html", translated_text=translated_text, html_with_entities=html_with_entities)

if __name__ == "__main__":
    app.run(debug=True)