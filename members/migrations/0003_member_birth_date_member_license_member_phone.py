# Generated by Django 5.0.7 on 2024-07-29 22:30

import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0002_alter_member_options_member_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="birth_date"),
        ),
        migrations.AddField(
            model_name="member",
            name="license",
            field=models.TextField(
                blank=True, max_length=250, null=True, verbose_name="license"
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None, verbose_name="phone"
            ),
        ),
    ]
