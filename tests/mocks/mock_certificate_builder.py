"""
Includes a `MockCertificateBuilder` class that mocks the `CertificateBuilder` class
"""
from __future__ import annotations
from io import BytesIO


class MockCertificateBuilder:
    def __init__(self: MockCertificateBuilder, settings: dict) -> None:
        """
        Initializes a MockCertificateBuilder to capture modifications made to certificate.
        """
        self.applied_changes = [f"Loaded settings"] if settings else []

    def draw_template(self: MockCertificateBuilder) -> MockCertificateBuilder:
        """
        Mock `draw_template`, recording the call.

        Returns:
            Itself for method chaining.
        """
        self.applied_changes.append("With template")
        return self

    def add_certificate_data(
        self: MockCertificateBuilder, certificate_data: object, certifier_data: object
    ) -> MockCertificateBuilder:
        """
        Mock `add_certificate_data`, recording the call.

        Args:
            certificate_data: The certificate data to record.
            certifier_data: The certifier data to record.
        Returns:
            Itself for method chaining.
        """
        self.applied_changes.append(
            f"With certified '{certificate_data.name}' and certifier '{certifier_data.name}'"
        )
        return self

    def add_qrcode(self: MockCertificateBuilder, url: str) -> MockCertificateBuilder:
        """
        Mock `add_qrcode`, recording the call.

        Args:
            url: The URL to record.
        Returns:
            Itself for method chaining.
        """
        self.applied_changes.append(f"With QR code to {url}")
        return self

    def save(self: MockCertificateBuilder) -> BytesIO:
        """
        Gets the bytes of a list-like string with the recorded calls.

        Returns:
            A list-like string with the recorded calls.
        """
        ret_text = "\n".join(self.applied_changes)
        out = BytesIO(bytes(ret_text, "utf-8"))
        out.seek(0)
        return out
