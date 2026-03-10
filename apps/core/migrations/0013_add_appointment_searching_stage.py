from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_require_due_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visaapplication",
            name="stage",
            field=models.CharField(
                choices=[
                    ("initial", "Initial"),
                    ("document_collected", "Document Collected"),
                    ("payment_requested", "Payment Requested"),
                    ("payment_received", "Payment Received"),
                    ("appointment_searching", "Appointment Searching"),
                    ("appointment_scheduled", "Appointment Scheduled"),
                    ("appointment_attended", "Appointment Attended"),
                    ("waiting_for_decision", "Waiting for Decision"),
                    ("decision_received", "Decision Received"),
                ],
                default="initial",
                max_length=30,
                verbose_name="Application Stage",
            ),
        ),
    ]
