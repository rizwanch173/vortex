from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_invoiceapplication_alter_invoice_visa_applications_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvoiceOtherPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=255, verbose_name="Description")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Amount")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("invoice", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="other_payments", to="core.invoice")),
            ],
            options={
                "verbose_name": "Invoice Other Payment",
                "verbose_name_plural": "Invoice Other Payments",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="invoiceotherpayment",
            index=models.Index(fields=["invoice"], name="core_invoic_invoice__b27f64_idx"),
        ),
        migrations.AddIndex(
            model_name="invoiceotherpayment",
            index=models.Index(fields=["-created_at"], name="core_invoic_created_5a4a86_idx"),
        ),
    ]
