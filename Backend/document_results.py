import base64
import os

import deepl
import spacy
from dotenv import load_dotenv
from mistralai import Mistral
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from spacy import displacy
from xhtml2pdf import pisa

load_dotenv()

API_KEY = os.getenv("API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
OCR_URL = os.getenv("OCR_URL")

# def save_html_to_pdf(source_html, output_filename):
#     """Convert HTML content to a PDF file."""
#     with open(output_filename, "w+b") as result_file:
#         pisa_status = pisa.CreatePDF(source_html, dest=result_file)
#     return pisa_status.err
#
# def save_text_to_pdf(text, filename):
#     c = canvas.Canvas(filename, pagesize=A4)
#     width, height = A4
#
#     margin_x = 50
#     margin_y = height - 50
#     line_height = 16
#
#     c.setFont("Times-Roman", 12)
#     paragraphs = text.split("\n")
#
#     for paragraph in paragraphs:
#         if not paragraph.strip():
#             margin_y -= line_height
#             continue
#
#         lines = simpleSplit(paragraph, "Times-Roman", 12, width - 2 * margin_x)
#
#         for line in lines:
#             c.drawString(margin_x, margin_y, line)
#             margin_y -= line_height
#             if margin_y < 50:
#                 c.showPage()
#                 c.setFont("Times-Roman", 12)
#                 margin_y = height - 50
#
#     c.save()


def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None


def getData(image_path):
    base64_image = encode_image(image_path)
    client = Mistral(api_key=API_KEY)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{base64_image}",
        },
    )

    result = ocr_response.pages[0].markdown

    # nlp_result = spacy.load("uk_core_news_trf")
    # doc_result = nlp_result(result)
    # html_res = displacy.render(doc_result, style="ent", page=True)
    # res_html_name = 'result_ner.html'
    # with open(res_html_name, "w", encoding="utf-8") as f:
    #     f.write(html_res)

    translator = deepl.Translator(DEEPL_API_KEY)
    translated_result = translator.translate_text(
        result, source_lang="UK", target_lang="EN-GB"
    ).text

    nlp_eng = spacy.load("en_core_web_trf")
    doc_eng = nlp_eng(translated_result)

    eng_html_name = "translated_result_ner.html"
    eng_html_path = os.path.join("static", "media", eng_html_name)
    html_eng = displacy.render(doc_eng, style="ent", page=True)
    with open(eng_html_path, "w", encoding="utf-8") as f:
        f.write(html_eng)
    # save_text_to_pdf(translated_result, "translated_result.pdf")
    # save_html_to_pdf(html_eng, "result_ner.pdf")
    return translated_result, eng_html_name
