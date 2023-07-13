from bs4 import BeautifulSoup
from PIL import Image
from pymongo import MongoClient
from qrcode import QRCode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape
import requests
from io import BytesIO
from os import environ

def get_database():
    # Connect to the MongoDB cluster
    CONNECTION_STRING = f'mongodb+srv://{environ["DB_USERNAME"]}:{environ["DB_PASSWORD"]}@{environ["DB_HOSTNAME"]}/?retryWrites=true&w=majority'
    client = MongoClient(CONNECTION_STRING)

    # Return "project2" database
    return client["project2"]

def check_metadata(url, name, content):
    # Retrieve URL
    response = requests.get(url) # error if url is invalid
    meta_elements = BeautifulSoup(response.text).find_all('meta')

    # Iterate over meta elements
    for element in meta_elements:
        # Check if the metadata information matches
        if element.attrs.get('name', None) == name and element.attrs.get('content', None) == content:
            return True
    
    # Metadata information did not match, so return false
    return False

def same_structure(dict1, dict2):
    if type(dict1) != dict or type(dict2) != dict():
        return type(dict1) == type(dict2)
    for key in dict1:
        if key not in dict2:
            return False
        if not same_structure(dict1[key], dict2[key]):
            return False
    return True

def get_certificate_pdf(certificate_data, certifier_data, settings, url):
    # Load default settings and compare them to settings by structure
    default_settings = {
        "template": "static/template.png",
        "font": {"name": "Poppins Bold", "size": 32},
        "qrcode": {"left": 600, "bottom": 100, "width": 125, "height": 125},
        "name": {"left": 390, "bottom": 310},
        "title": {"left": 322, "bottom": 245},
        "certifier": {"left": 377, "bottom": 115}
    }
    if not same_structure(settings, default_settings):
        settings = default_settings
    
    # Parse settings
    font_settings = settings["font"]
    qrcode_settings = settings["qrcode"]
    name_settings = {**settings["name"], "text": certificate_data["name"]}
    title_settings = {**settings["title"], "text": certificate_data["title"]}
    certifier_settings = {**settings["certifier"], "text": certifier_data["name"]}

    # Set page dimensions
    page_dimensions = landscape(A4)

    # Generate QR code and resize it
    qrcode_generator = QRCode(
        version=4,
        border=4,
    )
    qrcode_generator.add_data(url)
    qrcode_generator.make(fit=True)
    qrcode = qrcode_generator.make_image(
        fill_color="black",
        back_color="white",
    )
    qrcode = qrcode.resize((qrcode_settings["width"], qrcode_settings["height"]), Image.LANCZOS)

    # Open certificate template
    certificate_template = Image.open(BytesIO(requests.get(settings["template"]).content)) if settings["template"].startswith("http") else Image.open(settings["template"], 'r')
    certificate_template.resize((int(page_dimensions[0]), int(page_dimensions[1])),Image.LANCZOS)

    # Load font
    available_fonts = {
        "Poppins Bold": "static/Poppins-Bold.ttf"
    }
    font_path = available_fonts[font_settings["name"]] if font_settings["name"] in available_fonts else available_fonts["Poppins Bold"]
    pdfmetrics.registerFont(TTFont('Certificate Font', font_path))

    # Draw elements
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_dimensions)
    c.setFont('Certificate Font', font_settings["size"])
    c.drawImage(ImageReader(certificate_template), 0, 0, page_dimensions[0], page_dimensions[1])
    c.drawString(name_settings["left"], name_settings["bottom"], name_settings["text"])
    c.drawString(title_settings["left"], title_settings["bottom"], title_settings["text"])
    c.drawString(certifier_settings["left"], certifier_settings["bottom"], certifier_settings["text"])
    c.drawImage(ImageReader(qrcode), qrcode_settings["left"], qrcode_settings["bottom"], qrcode_settings["width"], qrcode_settings["height"])
    c.save()

    # Return buffer
    buffer.seek(0)
    return buffer