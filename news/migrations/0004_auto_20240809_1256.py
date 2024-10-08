# Generated by Django 5.0.7 on 2024-08-09 12:56

from django.db import migrations


def create_editors_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    try:
        Group.objects.create(name="editors")

    except:
        pass


def remove_editors_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    if Group.objects.get(name="editors").exists():
        Group.objects.get(name="editors").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_alter_newsitem_options"),
    ]

    operations = [migrations.RunPython(create_editors_group, remove_editors_group)]
