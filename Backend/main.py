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
                {'x': 10, 'y': 10},
                {'x': 320, 'y': 10},
                {'x': 320, 'y': 420},
                {'x': 10, 'y': 420}
            ]
            return render_template('scaner.html', points=points, fileupload=True,
                                   message=message)
        else:
            points = utils.array_to_json_format(four_points)
            message = 'Located the Cordinets of Document  '
            return render_template('scaner.html', points=points, fileupload=True, message=message)

    return render_template("scaner.html")


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
    translated_test, html_with_entities_name = document_results.getData(wrap_image_filepath)
    return render_template("file_translation.html", translated_test=translated_test, html_with_entities_name=html_with_entities_name)

if __name__ == "__main__":
    app.run(debug=True)