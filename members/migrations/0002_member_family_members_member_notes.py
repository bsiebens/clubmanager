# Generated by Django 5.1.3 on 2024-11-10 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="family_members",
            field=models.ManyToManyField(blank=True, to="members.member"),
        ),
        migrations.AddField(
            model_name="member",
            name="notes",
            field=models.TextField(blank=True, verbose_name="notes"),
        ),
    ]