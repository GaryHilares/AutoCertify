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
from app.utils import same_structure


class CertificateBuilder:
    """
    Provides functionality for building certificates. Each method except `save`
    returns `self` to allow for method chaining.
    """

    default_settings = {
        "template": "static/template.png",
        "font": {"name": "Poppins Bold", "size": 32},
        "qrcode": {"left": 600, "bottom": 100, "width": 125, "height": 125},
        "name": {"left": 390, "bottom": 310},
        "title": {"left": 322, "bottom": 245},
        "certifier": {"left": 377, "bottom": 115},
    }

    def __init__(self, settings: dict):
        """
        Creates a new CertificateBuilder with the provided settings.

        Arguments:
            settings (dict)
                Information about the layout of the generated certificate PDF.
        Returns:
            self (CertificateBuilder)
                A newly created `CertificateBuilder` instance.
        """
        self.settings = (
            settings
            if same_structure(settings, CertificateBuilder.default_settings)
            else CertificateBuilder.default_settings
        )
        self.buffer = BytesIO()
        self.pdf_drawer = canvas.Canvas(self.buffer, pagesize=landscape(A4))

    def draw_template(self):
        """
        Adds the template to the certificate. Assumes its information was provided
        through the settings when the object was created.

        Returns:
            self (CertificateBuilder)
                Returns itself for method chaining.
        """
        page_dimensions = landscape(A4)
        template_settings = self.settings["template"]
        certificate_template = (
            Image.open(BytesIO(requests.get(template_settings, timeout=3).content))
            if template_settings.startswith("http")
            else Image.open(template_settings, "r")
        )
        certificate_template.resize(
            (int(page_dimensions[0]), int(page_dimensions[1])), Image.LANCZOS
        )
        self.pdf_drawer.drawImage(
            ImageReader(certificate_template),
            0,
            0,
            page_dimensions[0],
            page_dimensions[1],
        )
        return self

    def add_certificate_data(self, certificate_data: dict, certifier_data: dict):
        """
        Arguments:
            certificate_data (dict)
                Information about the certificate, including the name and title.
            certifier_data (dict)
                Information about the certifier, including its name.
        Returns:
            self (CertificateBuilder)
                Returns itself for method chaining.
        """
        font_settings = self.settings["font"]
        name_settings = {**self.settings["name"], "text": certificate_data["name"]}
        title_settings = {**self.settings["title"], "text": certificate_data["title"]}
        certifier_settings = {
            **self.settings["certifier"],
            "text": certifier_data["name"],
        }

        # Load font
        available_fonts = {"Poppins Bold": "static/Poppins-Bold.ttf"}
        font_path = (
            available_fonts[font_settings["name"]]
            if font_settings["name"] in available_fonts
            else available_fonts["Poppins Bold"]
        )
        pdfmetrics.registerFont(TTFont("Certificate Font", font_path))
        self.pdf_drawer.setFont("Certificate Font", font_settings["size"])

        self.pdf_drawer.drawString(
            name_settings["left"], name_settings["bottom"], name_settings["text"]
        )
        self.pdf_drawer.drawString(
            title_settings["left"], title_settings["bottom"], title_settings["text"]
        )
        self.pdf_drawer.drawString(
            certifier_settings["left"],
            certifier_settings["bottom"],
            certifier_settings["text"],
        )
        return self

    def add_qrcode(self, url: str):
        """
        Adds QR code to generate PDF.

        Arguments:
            url (str)
                URL to create the certificate's QR.
        Returns:
            self (CertificateBuilder)
                Returns itself for method chaining.
        """
        qrcode_settings = self.settings["qrcode"]

        # Generate QR code and resize it
        qrcode_generator = QRCode(version=4, border=4)
        qrcode_generator.add_data(url)
        qrcode_generator.make(fit=True)
        qrcode = qrcode_generator.make_image(
            fill_color="black",
            back_color="white",
        )
        qrcode = qrcode.resize(
            (qrcode_settings["width"], qrcode_settings["height"]), Image.LANCZOS
        )
        self.pdf_drawer.drawImage(
            ImageReader(qrcode),
            qrcode_settings["left"],
            qrcode_settings["bottom"],
            qrcode_settings["width"],
            qrcode_settings["height"],
        )
        return self

    def save(self) -> BytesIO:
        """
        Saves a PDF certificate with the object's information.

        Returns:
            Bytes of the generated PDF.
        """
        self.pdf_drawer.save()
        self.buffer.seek(0)
        return self.buffer
