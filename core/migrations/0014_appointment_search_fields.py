from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_add_appointment_searching_stage"),
    ]

    operations = [
        migrations.AddField(
            model_name="visaapplication",
            name="appointment_search_email",
            field=models.EmailField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Appointment Search Email",
            ),
        ),
        migrations.AddField(
            model_name="visaapplication",
            name="appointment_search_website",
            field=models.URLField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name="Appointment Website",
            ),
        ),
    ]
