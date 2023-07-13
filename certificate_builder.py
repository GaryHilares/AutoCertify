"""
FILE
    certificate_builder.py
DESCRIPTION
    Provides utilities for the "Certificate Automation" Flask app. This
    includes building PDF certificates from JSON options.
"""
from io import BytesIO
from PIL import Image
from qrcode import QRCode
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape
import requests
from utils import same_structure


def get_certificate_pdf(
    certificate_data: dict, certifier_data: dict, settings: dict, url: str
) -> BytesIO:
    """
    Creates a PDF certificate with the information passed.

    Arguments:
        certificate_data (dict)
            Information about the certificate, including the name and title.
        certifier_data (dict)
            Information about the certifier, including its name.
        settings (dict)
            Information about the layout of the generated certificate PDF.
        url (str)
            URL to create the certificate's QR.
    Returns:
        Bytes of the generated PDF.
    """
    # Load default settings and use them if settings are incomplete
    default_settings = {
        "template": "static/template.png",
        "font": {"name": "Poppins Bold", "size": 32},
        "qrcode": {"left": 600, "bottom": 100, "width": 125, "height": 125},
        "name": {"left": 390, "bottom": 310},
        "title": {"left": 322, "bottom": 245},
        "certifier": {"left": 377, "bottom": 115},
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
    qrcode = qrcode.resize(
        (qrcode_settings["width"], qrcode_settings["height"]), Image.LANCZOS
    )

    # Open certificate template
    certificate_template = (
        Image.open(BytesIO(requests.get(settings["template"], timeout=3).content))
        if settings["template"].startswith("http")
        else Image.open(settings["template"], "r")
    )
    certificate_template.resize(
        (int(page_dimensions[0]), int(page_dimensions[1])), Image.LANCZOS
    )

    # Load font
    available_fonts = {"Poppins Bold": "static/Poppins-Bold.ttf"}
    font_path = (
        available_fonts[font_settings["name"]]
        if font_settings["name"] in available_fonts
        else available_fonts["Poppins Bold"]
    )
    pdfmetrics.registerFont(TTFont("Certificate Font", font_path))

    # Draw elements
    buffer = BytesIO()
    pdf_drawer = canvas.Canvas(buffer, pagesize=page_dimensions)
    pdf_drawer.setFont("Certificate Font", font_settings["size"])
    pdf_drawer.drawImage(
        ImageReader(certificate_template), 0, 0, page_dimensions[0], page_dimensions[1]
    )
    pdf_drawer.drawString(
        name_settings["left"], name_settings["bottom"], name_settings["text"]
    )
    pdf_drawer.drawString(
        title_settings["left"], title_settings["bottom"], title_settings["text"]
    )
    pdf_drawer.drawString(
        certifier_settings["left"],
        certifier_settings["bottom"],
        certifier_settings["text"],
    )
    pdf_drawer.drawImage(
        ImageReader(qrcode),
        qrcode_settings["left"],
        qrcode_settings["bottom"],
        qrcode_settings["width"],
        qrcode_settings["height"],
    )
    pdf_drawer.save()

    # Return buffer
    buffer.seek(0)
    return buffer
