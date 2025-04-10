from http import HTTPStatus

import cv2
import numpy as np
import spacy
from flask import Flask, request, jsonify, redirect, url_for, flash
from flask import render_template
from spacy import displacy

import document_results  # Assuming this is a custom module for document results
import passport_results  # Assuming this is a custom module for passport results
import settings
import utils

app = Flask(__name__)
app.secret_key = "document_scanner_app"

docscan = utils.DocumentScan()

DEFAULT_POINTS = [
    {"x": 0, "y": 0},
    {"x": 10, "y": 0},
    {"x": 0, "y": 10},
    {"x": 10, "y": 10},
]

@app.route("/")
def index():
    """Render the homepage of the document scanner application."""
    return render_template("index.html")


@app.route("/about")
def about():
    """Render the about page with application information."""
    return render_template("about.html")


@app.route("/scan", methods=["GET", "POST"])
def scandoc():
    """
    Handle document scanning functionality.

    Returns:
        Rendered template with scan results or error message.
    """
    if request.method == "POST":
        if "image_name" not in request.files:
            return jsonify({"error": "No file part"}), HTTPStatus.BAD_REQUEST
        file = request.files["image_name"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), HTTPStatus.BAD_REQUEST
        try:
            upload_image_path = utils.save_upload_image(file)
            # print("Img save in =", upload_image_path)
            # predict the coordinates
            four_points, size = docscan.document_scanner(upload_image_path)
            # print(four_points, size)
            if four_points is None:
                message = "UNABLE TO LOCATE THE COORDINATES"
                return render_template(
                    "scaner.html",
                    points=DEFAULT_POINTS,
                    fileupload=True,
                    message=message
                )

            points = utils.array_to_json_format(four_points)
            message = "Located the Coordinates of Document"
            return render_template(
                "scaner.html",
                points=points,
                fileupload=True,
                message=message
            )
        except Exception as e:
            flash(f"Error processing image: {str(e)}", "error")
            return redirect(request.url)

    return render_template("scaner.html")


@app.route("/scandoc", methods=["GET", "POST"])
def scan():
    """
    Alternative document scanning endpoint with different template.

    Returns:
        Rendered template with scan results or error message.
    """
    if request.method == "POST":
        if "image_name" not in request.files:
            return jsonify({"error": "No file part"}), HTTPStatus.BAD_REQUEST

        file = request.files["image_name"]
        if not file or file.filename == "":
            return jsonify({"error": "No file selected"}), HTTPStatus.BAD_REQUEST
        try:
            upload_image_path = utils.save_upload_image(file)
            four_points, size = docscan.document_scanner(upload_image_path)

            if four_points is None:
                message = "UNABLE TO LOCATE THE COORDINATES"
                return render_template(
                    "scanerdoc.html",
                    points=DEFAULT_POINTS,
                    fileupload=True,
                    message=message
                )

            points = utils.array_to_json_format(four_points)
            message = "Located the Coordinates of Document"
            return render_template(
                "scanerdoc.html",
                points=points,
                fileupload=True,
                message=message
            )
        except Exception as e:
            return jsonify({"error": f"Processing failed: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR

    return render_template("scanerdoc.html")


@app.route("/transform", methods=["POST"])
def transform():
    """
    Transform the scanned document based on provided points.

    Returns:
        str: 'success' on successful transformation, 'fail' on error.
    """
    try:
        if not request.json or "data" not in request.json:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST

        points = request.json["data"]
        array = np.array(points)
        magic_color = docscan.calibrate_to_original_size(array)

        # utils.save_image(magic_color,'magic_color.jpg')
        filename = "magic_color.jpg"
        magic_image_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(magic_image_path, magic_color)

        return "success"
    except Exception as e:
        app.logger.error(f"Transform error: {str(e)}")
        return "fail", HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/prediction")
def prediction():
    """
    Display passport scan results.

    Returns:
        Rendered template with prediction results.
    """
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, "magic_color.jpg")
    try:
        results = passport_results.getData(wrap_image_filepath)
        return render_template("prediction.html", results=results)
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/file_translation")
def file_translation():
    """
    Process and redirect to translation results.

    Returns:
        Redirect to file_translation_results with translation data.
    """
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, "magic_color.jpg")
    try:
        translated_text, html_with_entities_name = document_results.getData(wrap_image_filepath)
        html_filepath = settings.join_path(settings.MEDIA_DIR, html_with_entities_name)
        return redirect(url_for(
            "file_translation_results",
            translated_text=translated_text,
            html_filepath=html_filepath
        ))
    except Exception as e:
        return jsonify({"error": f"Translation error: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/file_translation_results")
def file_translation_results():
    """
    Display translation results with named entity recognition.

    Returns:
        Rendered template with translated text and NER visualization.
    """
    translated_text = request.args.get("translated_text")
    html_filepath = request.args.get("html_filepath")

    try:
        with open(html_filepath, "r", encoding="utf-8") as f:
            html_with_entities = f.read()

        return render_template(
            "file_translation.html",
            translated_text=translated_text,
            html_with_entities=html_with_entities,
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/save_translation", methods=["POST"])
def save_translation():
    """
    Save edited translation text with NER visualization.

    Returns:
        Redirect to file_translation_results with updated data.
    """
    edited_text = request.form.get("edited_text")
    if not edited_text:
        return "No text provided", 400

    try:
        nlp_eng = spacy.load("en_core_web_trf")
        doc_eng = nlp_eng(edited_text)

        eng_html_name = "translated_result_ner.html"
        eng_html_path = settings.join_path(settings.MEDIA_DIR, eng_html_name)
        html_eng = displacy.render(doc_eng, style="ent", page=True)

        with open(eng_html_path, "w", encoding="utf-8") as f:
            f.write(html_eng)

        return redirect(url_for(
            "file_translation_results",
            translated_text=edited_text,
            html_filepath=eng_html_path
        ))
    except Exception as e:
        return jsonify({"error": f"Error saving translation: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/send-test-email', methods=['POST'])
def test_email():
    """
    Send a test email based on provided JSON data.

    Returns:
        JSON response with email sending result.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["to", "subject", "body"]):
            return jsonify({"error": "Missing required fields"}), HTTPStatus.BAD_REQUEST

        to_address = data["to"]
        subject = data["subject"]
        body = data["body"]
        result = utils.send_mail(to_address, subject, body)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Email sending failed: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(debug=True)
