# Generated by Django 5.1.1 on 2024-09-08 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0009_auto_20240908_1524"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="game_id",
            field=models.CharField(
                blank=True, max_length=250, null=True, verbose_name="game ID"
            ),
        ),
    ]
