import base64
import spacy
from mistralai import Mistral
from spacy import displacy
import deepl
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
OCR_URL = os.getenv("OCR_URL")
IMAGE_PATH = os.getenv("IMAGE_PATH")


def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None


base64_image = encode_image(IMAGE_PATH)
client = Mistral(api_key=API_KEY)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_image}"
    }
)

result = ocr_response.pages[0].markdown

nlp = spacy.load("uk_core_news_trf")
doc = nlp(result)
html = displacy.render(doc, style="ent", page=True)
with open("ner_output.html", "w", encoding="utf-8") as f:
    f.write(html)

translator = deepl.Translator(DEEPL_API_KEY)
text_eng = translator.translate_text(result, source_lang="UK", target_lang="EN-US").text

nlp_eng = spacy.load("en_core_web_sm")
doc_eng = nlp_eng(text_eng)

html_eng = displacy.render(doc_eng, style="ent", page=True)
with open("ner_output_eng.html", "w", encoding="utf-8") as f:
    f.write(html_eng)
