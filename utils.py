from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from os import environ
from io import BytesIO
from base64 import b64encode
from qrcode import QRCode
from PIL import Image, ImageFont, ImageDraw

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

def get_qrcode_in_base64(url, certificate_data, certifier_data):
    font_settings = {"path": "static/Poppins-Bold.ttf", "size": 48}
    qrcode_settings = {"left": 900, "top": 550, "width": 200, "height": 200}
    name_settings = {"left": 643, "top": 380, "text": certificate_data["name"]}
    title_settings = {"left": 643, "top": 485, "text": certificate_data["title"]}
    certifier_settings = {"left": 643, "top": 685, "text": certifier_data["name"]}

    # Create bytes buffer
    buffer = BytesIO()

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

    # Load font
    font = ImageFont.truetype(font_settings["path"], font_settings["size"])

    # Create drawing tool object
    drawing_tool = ImageDraw.Draw(certificate_template)

    # Write the name of the certified person
    _, _, name_width, _ = drawing_tool.textbbox((0, 0), name_settings["text"], font)
    drawing_tool.text((name_settings["left"] - name_width//2, name_settings["top"]), name_settings["text"], (0, 0, 0), font)

    # Write the name of the title
    _, _, title_width, _ = drawing_tool.textbbox((0, 0), title_settings["text"], font)
    drawing_tool.text((title_settings["left"] - title_width//2, title_settings["top"]), title_settings["text"], (0, 0, 0), font)

    # Write the name of the certifier
    _, _, certifier_width, _ = drawing_tool.textbbox((0, 0), certifier_settings["text"], font)
    drawing_tool.text((certifier_settings["left"] - certifier_width//2, certifier_settings["top"]), certifier_settings["text"], (0, 0, 0), font)

    # Paste QR code in certificate
    certificate_template.paste(qrcode, (qrcode_settings["left"], qrcode_settings["top"]))

    # Write certificate to bytes buffer
    certificate_template.save(buffer, "png")

    # Encode buffer in a base64 string
    b64_img = b64encode(buffer.getvalue()).decode()

    # Convert b64 string to data URI
    return "data:image/png;base64,{}".format(b64_img)