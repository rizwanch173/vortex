from django.db import migrations


def add_turkey_evisa_pricing(apps, schema_editor):
    Pricing = apps.get_model("core", "Pricing")
    defaults = {"amount": 50.00, "currency": "GBP", "is_active": True}
    pricing, created = Pricing.objects.get_or_create(visa_type="turkey_evisa", defaults=defaults)
    if not created:
        updated = False
        if pricing.amount != defaults["amount"]:
            pricing.amount = defaults["amount"]
            updated = True
        if pricing.currency != defaults["currency"]:
            pricing.currency = defaults["currency"]
            updated = True
        if pricing.is_active is not True:
            pricing.is_active = True
            updated = True
        if updated:
            pricing.save(update_fields=["amount", "currency", "is_active"])


def remove_turkey_evisa_pricing(apps, schema_editor):
    Pricing = apps.get_model("core", "Pricing")
    Pricing.objects.filter(visa_type="turkey_evisa").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_appointment_search_fields"),
    ]

    operations = [
        migrations.RunPython(add_turkey_evisa_pricing, remove_turkey_evisa_pricing),
    ]
