from django.db import migrations, models
from django.utils import timezone


def set_due_date(apps, schema_editor):
    Invoice = apps.get_model("core", "Invoice")
    for invoice in Invoice.objects.filter(due_date__isnull=True):
        invoice.due_date = invoice.invoice_date or invoice.created_at.date() or timezone.localdate()
        invoice.save(update_fields=["due_date"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_add_auto_ids"),
    ]

    operations = [
        migrations.RunPython(set_due_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="invoice",
            name="due_date",
            field=models.DateField(
                help_text="Payment due date",
                verbose_name="Due Date",
            ),
        ),
    ]
