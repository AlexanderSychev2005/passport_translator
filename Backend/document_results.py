import base64
import os

import deepl
import spacy
from dotenv import load_dotenv
from mistralai import Mistral
from spacy import displacy

load_dotenv()

API_KEY = os.getenv("API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
OCR_URL = os.getenv("OCR_URL")


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
    """Extract text from an image, translate it to English, and generate NER HTML.

    Args:
        image_path (str): Path to the image file to process.

    Returns:
        Tuple[str, str]: Translated text and the filename of the NER HTML file.

    Raises:
        ValueError: If image encoding or OCR processing fails.
        deepl.DeepLException: If translation fails.
    """
    base64_image = encode_image(image_path)
    if base64_image is None:
        raise ValueError("Image encoding failed.")
    client = Mistral(api_key=API_KEY)

    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}",
            },
        )
        result = ocr_response.pages[0].markdown
        print(result)
    except Exception as e:
        raise ValueError(f"OCR processing failed: {e}")

    translator = deepl.Translator(DEEPL_API_KEY)
    try:
        translated_result = translator.translate_text(
            result, target_lang="EN-GB"
        ).text
    except deepl.DeepLException as e:
        raise deepl.DeepLException(f"Translation failed: {e}")

    nlp_eng = spacy.load("en_core_web_trf")
    doc_eng = nlp_eng(translated_result)

    eng_html_name = "translated_result_ner.html"
    eng_html_path = os.path.join("static", "media", eng_html_name)
    html_eng = displacy.render(doc_eng, style="ent", page=True)

    os.makedirs(os.path.dirname(eng_html_path), exist_ok=True)

    with open(eng_html_path, "w", encoding="utf-8") as f:
        f.write(html_eng)
    return translated_result, eng_html_name
