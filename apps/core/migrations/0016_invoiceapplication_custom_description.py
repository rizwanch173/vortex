from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_add_turkey_evisa_pricing'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceapplication',
            name='custom_description',
            field=models.CharField(
                blank=True,
                help_text='Optional override for the invoice line item description',
                max_length=255,
                null=True,
                verbose_name='Custom Description',
            ),
        ),
    ]
