from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_invoiceotherpayment"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="client_id",
            field=models.CharField(
                blank=True,
                max_length=32,
                null=True,
                unique=True,
                verbose_name="Client ID",
            ),
        ),
        migrations.AddField(
            model_name="client",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("other", "Other/Unknown"),
                ],
                default="other",
                max_length=10,
                verbose_name="Gender",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="invoice_id",
            field=models.CharField(
                blank=True,
                max_length=96,
                null=True,
                unique=True,
                verbose_name="Invoice ID",
            ),
        ),
        migrations.AddField(
            model_name="visaapplication",
            name="application_id",
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                unique=True,
                verbose_name="Application ID",
            ),
        ),
    ]
