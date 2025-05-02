from http import HTTPStatus

import cv2
import numpy as np
import spacy
from flask import Flask, request, jsonify, redirect, url_for, flash
from flask import render_template
from spacy import displacy
import os
from datetime import datetime
import difflib
import re

import document_results
import passport_results
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
    if request.method == "POST":
        if "image_name" not in request.files:
            return jsonify({"error": "No file part"}), HTTPStatus.BAD_REQUEST
        file = request.files["image_name"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), HTTPStatus.BAD_REQUEST
        try:
            upload_image_path = utils.save_upload_image(file)
            four_points, size = docscan.document_scanner(upload_image_path)
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
    try:
        if not request.json or "data" not in request.json:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST
        points = request.json["data"]
        array = np.array(points)
        magic_color = docscan.calibrate_to_original_size(array)
        filename = "magic_color.jpg"
        magic_image_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(magic_image_path, magic_color)
        return "success"
    except Exception as e:
        app.logger.error(f"Transform error: {str(e)}")
        return "fail", HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/prediction")
def prediction():
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, "magic_color.jpg")
    try:
        results = passport_results.getData(wrap_image_filepath)
        return render_template("prediction.html", results=results)
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/file_translation")
def file_translation():
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, "magic_color.jpg")
    try:
        translated_text, html_with_entities_name = document_results.getData(wrap_image_filepath)
        html_filepath = settings.join_path(settings.MEDIA_DIR, html_with_entities_name)
        # Зберігаємо початковий текст у current_text.txt
        current_text_path = settings.join_path(settings.MEDIA_DIR, "current_text.txt")
        with open(current_text_path, "w", encoding="utf-8") as f:
            f.write(translated_text)

        # Очищаємо файл changelog.md одразу після сканування та перекладу
        changelog_path = settings.join_path(settings.MEDIA_DIR, "changelog.md")
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write("")

        return redirect(url_for(
            "file_translation_results",
            translated_text=translated_text,
            html_filepath=html_filepath
        ))
    except Exception as e:
        return jsonify({"error": f"Translation error: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/file_translation_results")
def file_translation_results():
    translated_text = request.args.get("translated_text")
    html_filepath = request.args.get("html_filepath")
    try:
        with open(html_filepath, "r", encoding="utf-8") as f:
            html_with_entities = f.read()
        # Читаємо журнал змін
        changelog_path = settings.join_path(settings.MEDIA_DIR, "changelog.md")
        changelog_content = ""
        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                changelog_content = f.read()
        return render_template(
            "file_translation.html",
            translated_text=translated_text,
            html_with_entities=html_with_entities,
            changelog=changelog_content
        )
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/save_translation", methods=["POST"])
def save_translation():
    edited_text = request.form.get("edited_text")
    if not edited_text:
        return "No text provided", 400
    try:
        # Завантажуємо попередній текст для порівняння
        current_text_path = settings.join_path(settings.MEDIA_DIR, "current_text.txt")
        previous_text = ""
        if os.path.exists(current_text_path):
            with open(current_text_path, "r", encoding="utf-8") as f:
                previous_text = f.read().strip()

        # Зберігаємо поточний текст у current_text.txt
        with open(current_text_path, "w", encoding="utf-8") as f:
            f.write(edited_text)

        # Формуємо запис у журнал змін
        changelog_path = settings.join_path(settings.MEDIA_DIR, "changelog.md")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        changelog_entry = f"<h2>Change on {current_time}</h2>\n"

        # Порівнюємо тексти
        previous_sentences = re.split(r'(?<=[.!?])\s+', previous_text.strip()) if previous_text else []
        new_sentences = re.split(r'(?<=[.!?])\s+', edited_text.strip())

        # Додаємо речення до списків для порівняння
        max_len = max(len(previous_sentences), len(new_sentences))
        previous_sentences.extend([""] * (max_len - len(previous_sentences)))
        new_sentences.extend([""] * (max_len - len(new_sentences)))

        # Порівнюємо речення
        changed = False
        for prev_sent, new_sent in zip(previous_sentences, new_sentences):
            # Нормалізуємо речення перед порівнянням
            prev_sent_normalized = " ".join(prev_sent.strip().split()) if prev_sent else ""
            new_sent_normalized = " ".join(new_sent.strip().split()) if new_sent else ""

            # Перевіряємо, чи є різниця між реченнями
            if prev_sent_normalized != new_sent_normalized and prev_sent_normalized and new_sent_normalized:
                changed = True
                # Порівнюємо слова в змінених реченнях
                prev_words = prev_sent.split()
                new_words = new_sent.split()
                differ = difflib.Differ()
                diff = list(differ.compare(prev_words, new_words))

                # Формуємо речення з виділеними змінами
                highlighted_prev = []
                highlighted_new = []
                for word in diff:
                    word_text = word[2:]
                    if word.startswith("  "):  # Незмінене слово
                        highlighted_prev.append(word_text)
                        highlighted_new.append(word_text)
                    elif word.startswith("- "):  # Видалене слово
                        highlighted_prev.append(f'<span class="highlight-changed">{word_text}</span>')
                    elif word.startswith("+ "):  # Додане слово
                        highlighted_new.append(f'<span class="highlight-changed">{word_text}</span>')

                # Додаємо змінені речення до журналу
                changelog_entry += "<h3>Previous Sentence:</h3>\n<p>" + " ".join(highlighted_prev) + "</p>\n"
                changelog_entry += "<h3>New Sentence:</h3>\n<p>" + " ".join(highlighted_new) + "</p>\n"

        # Якщо змін не було, додаємо відповідне повідомлення
        if not changed:
            changelog_entry = ""  # Не додаємо запис, якщо змін немає

        # Читаємо існуючий журнал змін
        existing_changelog = ""
        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                existing_changelog = f.read()

        # Додаємо новий запис зверху, лише якщо є зміни
        if changelog_entry:
            updated_changelog = changelog_entry + "\n" + existing_changelog
        else:
            updated_changelog = existing_changelog

        # Перезаписуємо журнал змін
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(updated_changelog)

        # Зберігаємо оновлений текст із NER
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