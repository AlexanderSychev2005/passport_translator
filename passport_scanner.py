import re
from datetime import datetime
import easyocr
import cv2
from reportlab.pdfbase.ttfonts import TTFont
from googletrans import Translator
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

translator = Translator()

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansBold', 'DejaVuSans-Bold.ttf'))

countries_map = {
    "UKR": "UKRAYNA", "TUR": "TÜRKİYE", "USA": "AMERİKA BİRLEŞİK DEVLETLERİ",
    "RUS": "RUSYA", "DEU": "ALMANYA", "FRA": "FRANSA"
}

month_translation = {
    "Jan": "OCAK", "Feb": "ŞUBAT", "Mar": "MART", "Apr": "NİSAN",
    "May": "MAYIS", "Jun": "HAZİRAN", "Jul": "TEMMUZ", "Aug": "AĞUSTOS",
    "Sep": "EYLÜL", "Oct": "EKİM", "Nov": "KASIM", "Dec": "ARALIK"
}


def save_to_file(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("DejaVuSansBold", 14)
    c.drawString(270, 750, data["DOĞUM YERİ"])
    c.setFont("DejaVuSansBold", 10)
    c.drawString(50, 700, "PASAPORT")
    c.drawString(170, 700, "P")
    c.drawString(190, 550, f"{data["CİNSİYETİ"]}")

    c.drawString(250, 670, f"{data["surname"]}")
    c.drawString(250, 640, f"{data["name"]}")
    c.drawString(250, 610, f"{data["UYRUĞU"]}")
    c.drawString(250, 580, f"{data["DOĞUM TARİHİ"]}")

    c.drawString(250, 520, f"{data["DÜZENLENME TARİHİ"]}")
    c.drawString(250, 490, f"{data["GEÇERLİLİK TARİHİ"]}")

    c.drawString(450, 700, f"{data["PASAPORT NO"]}")
    c.drawString(490, 520, f"{data["DÜZENLEYEN MAKAM"]}")
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

    c.drawString(250, 700, f"ÜLKE KODU: {data["ÜLKE KODU"]}")
    c.drawString(250, 550, f"DOĞUM YERİ:")

    c.drawString(370, 700, f"PASAPORT NO.:")
    c.drawString(370, 580, f"KAYIT NO.:{data["KAYIT NO"]}")
    c.drawString(370, 550, f"{data["DOĞUM YERİ"]}")
    c.drawString(370, 520, f"DÜZENLEYEN MAKAM:")

    c.setFont("DejaVuSans", 7)
    c.drawString(50, 470, data['MRZ'][:44])
    c.drawString(50, 450, data['MRZ'][44:])

    c.save()


image = cv2.imread("oleg_test.jpg")

detail = cv2.detailEnhance(image, sigma_s=20, sigma_r=0.15)
gray = cv2.cvtColor(detail, cv2.COLOR_BGR2GRAY)

# cv2.imshow("gray", gray)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

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
entities = {
    "Орган що видав/ Authority": re.search(r"(\d{4})", full_text),
    "MRZ": re.search(r"(P\s*<[^\n]*\d{2})", full_text),
}
filtered_entities = {k: v.group(1) if v else None for k, v in entities.items()}
filtered_entities['MRZ'] = filtered_entities['MRZ'].replace(" ", '')

mrz = filtered_entities['MRZ'].upper()

authority = filtered_entities['Орган що видав/ Authority']

mrz = mrz.replace("О", "O").replace("М", "M")
print(mrz)
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


def translate_date(date_str):
    day, month, year = date_str.split()
    month_turkish = month_translation.get(month, month)
    return f"{day} {month_turkish} {year}"

country_full = countries_map[country]
parsed_results = {
    "Country": f"{country}",
    "Surname": f"{surname}",
    "Name": f"{name}",
    "Passport number": f"{passport_number}",
    "Nationality": f"{nationality}",
    "Place of birth": f"{country_full}",
    "Date of birth": f"{translate_date(formatted_date)}",
    "Gender": "KADIN" if gender == 'F' else "ADAM",
    "Authority": f"{authority}",
    "Date of issue": f"{translate_date(formatted_date_issue)}",
    "Date of expiry": f"{translate_date(formatted_date_exp)}",
    "Record number": f"{personal_number[:8]}-{personal_number[8:]}",
    "mrz": mrz
}


parsed_data = {
    "ÜLKE KODU": country,
    "PASAPORT NO": passport_number,
    "SOYADI": surname,
    "ADI": name,
    "UYRUĞU": country,
    "DOĞUM TARİHİ": translate_date(formatted_date),
    "CİNSİYETİ": "KADIN" if gender == 'F' else "ADAM",
    "DOĞUM YERİ": country_full,
    "DÜZENLENME TARİHİ": translate_date(formatted_date_issue),
    "GEÇERLİLİK TARİHİ": translate_date(formatted_date_exp),
    "KAYIT NO": f"{personal_number[:8]}-{personal_number[8:]}",
    "DÜZENLEYEN MAKAM": authority,
    "MRZ": mrz
}
print(len(mrz))
#
# for i in parsed_data:
#     print(f"{i}: {parsed_data[i]}")
# print("\n")

save_to_file("passport_data.pdf", parsed_data)
# print("!!!")
