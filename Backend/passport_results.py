import re
from datetime import datetime
import easyocr
import cv2
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

# Register fonts
pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSansBold", "DejaVuSans-Bold.ttf"))

# Define translations for countries
COUNTRIES_TRANSLATION = {
    "UKR": "UKRAYNA",
    "TUR": "TÜRKİYE",
    "USA": "AMERİKA BİRLEŞİK DEVLETLERİ",
    "RUS": "RUSYA",
    "DEU": "ALMANYA",
    "FRA": "FRANSA",
}

# Define translations for months
MONTH_TRANSLATION = {
    "Jan": "OCAK",
    "Feb": "ŞUBAT",
    "Mar": "MART",
    "Apr": "NİSAN",
    "May": "MAYIS",
    "Jun": "HAZİRAN",
    "Jul": "TEMMUZ",
    "Aug": "AĞUSTOS",
    "Sep": "EYLÜL",
    "Oct": "EKİM",
    "Nov": "KASIM",
    "Dec": "ARALIK",
}


def translate_date(date_str):
    """
    Function to translate date from English to Turkish
    :param date_str: date string
    :return: date string in Turkish
    """
    try:
        day, month, year = date_str.split()
        month_turkish = MONTH_TRANSLATION.get(month, month)
        return f"{day} {month_turkish} {year}"
    except ValueError:
        return date_str


def save_to_file(filename, data):
    """
    Function to save passport data to a PDF file
    :param filename: filename of the file
    :param data: dictionary of passport data
    :return: None
    """
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DejaVuSansBold", "DejaVuSans-Bold.ttf"))
    except Exception as e:
        pdfmetrics.registerFont(TTFont("DejaVuSans", TTFont("Helvetica", "Helvetica")))
        pdfmetrics.registerFont(
            TTFont("DejaVuSansBold", TTFont("Helvetica-Bold", "Helvetica-Bold"))
        )

    c = canvas.Canvas(filename, pagesize=A4)

    required_keys = [
        "Full country",
        "Gender",
        "Surname",
        "Name",
        "Date of birth",
        "Date of issue",
        "Date of expiry",
        "Passport number",
        "Country",
        "Record number",
        "MRZ",
    ]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"Key '{key}' is missing in the data dictionary.")

    full_country = data["Full country"]
    gender = data["Gender"]
    surname = data["Surname"]
    name = data["Name"]
    date_of_birth = data["Date of birth"]
    date_of_issue = data["Date of issue"]
    date_of_expiry = data["Date of expiry"]
    passport_number = data["Passport number"]
    country = data["Country"]
    record_number = data["Record number"]
    mrz = data["MRZ"]

    c.setFont("DejaVuSansBold", 14)
    c.drawString(270, 750, full_country)

    c.setFont("DejaVuSansBold", 10)
    c.drawString(50, 700, "PASAPORT")
    c.drawString(170, 700, "P")

    c.drawString(190, 550, gender)
    c.drawString(250, 670, surname)
    c.drawString(250, 640, name)
    c.drawString(250, 610, full_country)
    c.drawString(250, 580, date_of_birth)
    c.drawString(370, 550, full_country)
    c.drawString(250, 520, date_of_issue)
    c.drawString(250, 490, date_of_expiry)
    c.drawString(450, 700, passport_number)

    c.drawString(130, 700, "TÜRÜ:")
    c.drawString(130, 670, "SOYADI:")
    c.drawString(130, 640, "ADI:")
    c.drawString(130, 610, "UYRUĞU:")
    c.drawString(130, 580, "DOĞUM TARİHİ:")
    c.drawString(130, 550, "CİNSİYETİ:")
    c.drawString(130, 520, "DÜZENLENME TARİHİ:")
    c.drawString(130, 490, "GEÇERLİLİK TARİHİ:")

    c.drawString(250, 700, f"ÜLKE KODU: {country}")
    c.drawString(250, 550, "DOĞUM YERİ:")

    c.drawString(370, 700, "PASAPORT NO.:")
    c.drawString(370, 580, f"KAYIT NO.: {record_number}")

    c.setFont("DejaVuSans", 7)
    if len(mrz) >= 44:
        c.drawString(50, 470, mrz[:44])
        c.drawString(50, 450, mrz[44:])
    else:
        c.drawString(50, 470, mrz)
        c.drawString(50, 450, "")

    c.setFont("DejaVuSans", 10)
    c.drawString(50, 600, "")

    c.save()


def extract_text_from_image(image_path):
    try:
        image = cv2.imread(image_path)
        reader = easyocr.Reader(["en", "uk"], gpu=True)
        result = reader.readtext(
            image,
            detail=0,
            contrast_ths=0.5,
            adjust_contrast=0.7,
            text_threshold=0.6,
            low_text=0.4,
            canvas_size=2000,
            decoder="wordbeamsearch",
        )
        if not result:
            raise ValueError("Text on the image is not recognised.")
        return " ".join(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def extract_mrz(full_text):
    full_text = full_text.replace(" ", "")
    mrz = re.search(r"(P\s*<[^\n]*\d{2})", full_text)
    mrz = mrz.group(0)
    mrz = mrz.replace(" ", "").upper()
    mrz = mrz.replace("О", "O").replace("М", "M")
    return mrz


def getData(file_path):
    try:
        full_text = extract_text_from_image(file_path)
        if not full_text:
            raise ValueError("No text found in the image.")
        mrz = extract_mrz(full_text)
        if not mrz:
            raise ValueError("No MRZ found in the text.")

        mrz_pattern = re.compile(
            r"P<(?P<country>[A-Z]{3})"
            r"(?P<surname>[A-Z]+)<<(?P<name>[A-Z]+)<+"
            r"(?P<passport_number>[A-Z0-9]{8})<+"
            r"."
            r"(?P<nationality>[A-Z]{3})"
            r"(?P<birth_date>\d{6})"
            r"."
            r"(?P<gender>[MF])"
            r"(?P<expiry_date>\d{6})"
            r"."
            r"(?P<personal_number>[A-Z0-9]{13})"
        )
        match = mrz_pattern.search(mrz)

        if match:
            country = match.group("country")
            name = match.group("name")
            surname = match.group("surname")
            passport_number = match.group("passport_number")
            nationality = match.group("nationality")
            birth_date = match.group("birth_date")
            gender = match.group("gender")
            expiry_date = match.group("expiry_date")
            personal_number = match.group("personal_number")
        else:
            raise ValueError("MRZ format is incorrect.")

        date_obj = datetime.strptime(birth_date, "%y%m%d")
        formatted_date = date_obj.strftime("%d %b %Y")

        date_obj_exp = datetime.strptime(expiry_date, "%y%m%d")
        formatted_date_exp = date_obj_exp.strftime("%d %b %Y")

        issue_date_obj = date_obj_exp.replace(year=date_obj_exp.year - 10)
        formatted_date_issue = issue_date_obj.strftime("%d %b %Y")

        country_full = COUNTRIES_TRANSLATION.get(country, country)
        parsed_results = {
            "Country": f"{country}",
            "Surname": f"{surname}",
            "Name": f"{name}",
            "Passport number": f"{passport_number}",
            "Nationality": f"{nationality}",
            "Full country": f"{country_full}",
            "Date of birth": f"{translate_date(formatted_date)}",
            "Gender": "KADIN" if gender == "F" else "ADAM",
            "Date of issue": f"{translate_date(formatted_date_issue)}",
            "Date of expiry": f"{translate_date(formatted_date_exp)}",
            "Record number": f"{personal_number[:8]}-{personal_number[8:]}",
            "MRZ": mrz,
        }
        file_path = "./static/media/passport_data.pdf"
        save_to_file(file_path, parsed_results)
        return file_path
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
