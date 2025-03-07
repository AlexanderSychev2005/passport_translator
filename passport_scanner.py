import re
from datetime import datetime
import easyocr
import cv2
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

# Register fonts
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', 'DejaVuSans-Bold.ttf'))

# Define translations for countries
COUNTRIES_TRANSLATION = {
    "UKR": "UKRAYNA", "TUR": "TÜRKİYE", "USA": "AMERİKA BİRLEŞİK DEVLETLERİ",
    "RUS": "RUSYA", "DEU": "ALMANYA", "FRA": "FRANSA"
}

# Define translations for months
MONTH_TRANSLATION = {
    "Jan": "OCAK", "Feb": "ŞUBAT", "Mar": "MART", "Apr": "NİSAN",
    "May": "MAYIS", "Jun": "HAZİRAN", "Jul": "TEMMUZ", "Aug": "AĞUSTOS",
    "Sep": "EYLÜL", "Oct": "EKİM", "Nov": "KASIM", "Dec": "ARALIK"
}


def translate_date(date_str):
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
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("DejaVuSansBold", 14)
    c.drawString(270, 750, data["Full country"])
    c.setFont("DejaVuSansBold", 10)
    c.drawString(50, 700, "PASAPORT")
    c.drawString(170, 700, "P")
    c.drawString(190, 550, f"{data["Gender"]}")

    c.drawString(250, 670, f"{data["Surname"]}")
    c.drawString(250, 640, f"{data["Name"]}")
    c.drawString(250, 610, f"{data["Full country"]}")
    c.drawString(250, 580, f"{data["Date of birth"]}")
    c.drawString(370, 550, f"{data["Full country"]}")
    c.drawString(250, 520, f"{data["Date of issue"]}")
    c.drawString(250, 490, f"{data["Date of expiry"]}")

    c.drawString(450, 700, f"{data["Passport number"]}")
    c.drawString(490, 520, f"{data["Authority"]}")
    c.setFont("DejaVuSans", 10)

    c.drawString(50, 600, "")

    c.drawString(130, 700, "TÜRÜ:")
    c.drawString(130, 670, "SOYADI:")
    c.drawString(130, 640, "ADI:")
    c.drawString(130, 610, "UYRUĞU:")
    c.drawString(130, 580, "DOĞUM TARİHİ:")
    c.drawString(130, 550, f"CİNSİYETİ:")
    c.drawString(130, 520, "DÜZENLENME TARİHİ:")
    c.drawString(130, 490, "GEÇERLİLİK TARİHİ:")

    c.drawString(250, 700, f"ÜLKE KODU: {data["Country"]}")
    c.drawString(250, 550, f"DOĞUM YERİ:")

    c.drawString(370, 700, f"PASAPORT NO.:")
    c.drawString(370, 580, f"KAYIT NO.:{data["Record number"]}")
    c.drawString(370, 520, f"DÜZENLEYEN MAKAM:")

    c.setFont("DejaVuSans", 7)
    c.drawString(50, 470, data['MRZ'][:44])
    c.drawString(50, 450, data['MRZ'][44:])

    c.save()


def extract_text_from_image(image_path):
    try:
        image = cv2.imread(image_path)
        reader = easyocr.Reader(['en', 'uk'], gpu=True)
        result = reader.readtext(image,
                                 detail=0,
                                 contrast_ths=0.5,
                                 adjust_contrast=0.7,
                                 text_threshold=0.6,
                                 low_text=0.4,
                                 canvas_size=2000,
                                 decoder='wordbeamsearch')
        full_text = " ".join(result)
        return full_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_authority(full_text):
    authority = re.search(r"(\s+\d{4}\s+)", full_text)
    authority = authority.group(0)
    return authority


def extract_mrz(full_text):
    mrz = re.search(r"(P\s*<[^\n]*\d{2})", full_text)
    mrz = mrz.group(0)
    mrz = mrz.replace(" ", '').upper()
    mrz = mrz.replace("О", "O").replace("М", "M")
    return mrz


def main():
    full_text = extract_text_from_image("oleg_test.jpg")
    if not full_text:
        print("No text found in the image.")
        return
    authority = extract_authority(full_text)
    if not authority:
        print("Authority not found in the text.")
        return
    mrz = extract_mrz(full_text)
    if not mrz:
        print("MRZ not found in the text.")
        return

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

    date_obj = datetime.strptime(birth_date, "%y%m%d")
    formatted_date = date_obj.strftime("%d %b %Y")

    date_obj_exp = datetime.strptime(expiry_date, "%y%m%d")
    formatted_date_exp = date_obj_exp.strftime("%d %b %Y")

    issue_date_obj = date_obj_exp.replace(year=date_obj_exp.year - 10)
    formatted_date_issue = issue_date_obj.strftime("%d %b %Y")

    country_full = COUNTRIES_TRANSLATION[country]
    parsed_results = {
        "Country": f"{country}",
        "Surname": f"{surname}",
        "Name": f"{name}",
        "Passport number": f"{passport_number}",
        "Nationality": f"{nationality}",
        "Full country": f"{country_full}",
        "Date of birth": f"{translate_date(formatted_date)}",
        "Gender": "KADIN" if gender == 'F' else "ADAM",
        "Authority": f"{authority}",
        "Date of issue": f"{translate_date(formatted_date_issue)}",
        "Date of expiry": f"{translate_date(formatted_date_exp)}",
        "Record number": f"{personal_number[:8]}-{personal_number[8:]}",
        "MRZ": mrz
    }

    save_to_file("passport_data.pdf", parsed_results)


if __name__ == "__main__":
    main()
