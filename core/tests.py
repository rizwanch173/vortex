from datetime import date
from unittest.mock import patch

from django.test import TestCase

from core.models import Client, Invoice, InvoiceApplication, VisaApplication


class AutoIdGenerationTests(TestCase):
    def _create_client(self, suffix="1", **overrides):
        defaults = {
            "first_name": "Muhammad",
            "last_name": "Rizwan",
            "email": f"test{suffix}@example.com",
            "phone": "1234567890",
            "date_of_birth": date(1999, 5, 9),
            "gender": "male",
            "passport_number": f"P{suffix}12345",
            "nationality": "Pakistani",
            "country_of_residence": "Pakistan",
        }
        defaults.update(overrides)
        return Client.objects.create(**defaults)

    def test_client_id_generation_and_collision(self):
        with patch("core.models.timezone.localdate", return_value=date(2025, 12, 30)):
            client_one = self._create_client(suffix="1")
            self.assertEqual(client_one.client_id, "RA25123099")

            client_two = self._create_client(suffix="2")
            self.assertEqual(client_two.client_id, "RA2512309901")

    def test_application_id_generation_and_collision(self):
        with patch("core.models.timezone.localdate", return_value=date(2025, 12, 30)):
            client = self._create_client(suffix="3")
            app_one = VisaApplication.objects.create(
                client=client,
                visa_type="schengen",
                stage="initial",
            )
            self.assertEqual(app_one.application_id, "SRA25123099")

            app_two = VisaApplication.objects.create(
                client=client,
                visa_type="schengen",
                stage="initial",
            )
            self.assertEqual(app_two.application_id, "SRA2512309901")

    def test_invoice_id_order_and_collision(self):
        with patch("core.models.timezone.localdate", return_value=date(2025, 12, 30)):
            client = self._create_client(suffix="4")
            app_us = VisaApplication.objects.create(
                client=client,
                visa_type="us",
                stage="initial",
            )
            app_schengen = VisaApplication.objects.create(
                client=client,
                visa_type="schengen",
                stage="initial",
            )

            invoice_one = Invoice.objects.create(
                client=client,
                invoice_date=date(2025, 12, 30),
                due_date=date(2025, 12, 31),
            )
            InvoiceApplication.objects.create(
                invoice=invoice_one,
                visa_application=app_us,
                unit_price=150,
            )
            InvoiceApplication.objects.create(
                invoice=invoice_one,
                visa_application=app_schengen,
                unit_price=125,
            )
            invoice_one.refresh_from_db()
            self.assertEqual(invoice_one.invoice_id, "USRA-25123099-1231")

            invoice_two = Invoice.objects.create(
                client=client,
                invoice_date=date(2025, 12, 30),
                due_date=date(2025, 12, 31),
            )
            InvoiceApplication.objects.create(
                invoice=invoice_two,
                visa_application=app_us,
                unit_price=150,
            )
            InvoiceApplication.objects.create(
                invoice=invoice_two,
                visa_application=app_schengen,
                unit_price=125,
            )
            invoice_two.refresh_from_db()
            self.assertEqual(invoice_two.invoice_id, "USRA-25123099-1231-01")
