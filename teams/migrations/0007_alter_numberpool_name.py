# Generated by Django 5.1.3 on 2024-11-29 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0006_create_default_numberpool"),
    ]

    operations = [
        migrations.AlterField(
            model_name="numberpool",
            name="name",
            field=models.CharField(max_length=255, unique=True, verbose_name="name"),
        ),
    ]