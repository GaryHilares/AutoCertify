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

def get_certificate_pdf(certificate_data, certifier_data, url):
    font_settings = {"path": "static/Poppins-Bold.ttf", "size": 32}
    qrcode_settings = {"left": 600, "bottom": 100, "width": 125, "height": 125}
    name_settings = {"left": 390, "bottom": 310, "text": certificate_data["name"]}
    title_settings = {"left": 322, "bottom": 245, "text": certificate_data["title"]}
    certifier_settings = {"left": 377, "bottom": 115, "text": certifier_data["name"]}

    # Set page dimensions
    page_dimensions = landscape(A4)

    # Set QR generator information
    qrcode_generator = QRCode(
        version=4,
        border=4,
    )
    
    # Add data to QR code generator
    qrcode_generator.add_data(url)

    # Compile QR generator
    qrcode_generator.make(fit=True)

    # Generate QR code
    qrcode = qrcode_generator.make_image(
        fill_color="black",
        back_color="white",
    )

    # Resize the QR code
    qrcode = qrcode.resize((qrcode_settings["width"], qrcode_settings["height"]), Image.LANCZOS)

    # Open certificate template
    certificate_template = Image.open("static/template.png", 'r')
    certificate_template.resize((int(page_dimensions[0]), int(page_dimensions[1])),Image.LANCZOS)

    # Load font
    pdfmetrics.registerFont(TTFont('Certificate Font', font_settings["path"]))

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

    buffer.seek(0)
    return buffer