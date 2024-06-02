# Generated by Django 5.0.2 on 2024-05-30 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0009_alter_product_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]