# Generated by Django 5.0.7 on 2024-08-15 16:25

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0014_alter_member_emergency_phone_primary"),
        ("teams", "0005_alter_teamrole_options_teamrole_abbreviation_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="members",
            field=models.ManyToManyField(
                through="teams.TeamMembership",
                to="members.member",
                verbose_name="members",
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="name",
            field=models.CharField(default="test", max_length=250, verbose_name="name"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="team",
            name="short_name",
            field=models.CharField(
                blank=True,
                help_text="An optional short name",
                max_length=250,
                null=True,
                verbose_name="short name",
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="slug",
            field=django_extensions.db.fields.AutoSlugField(
                blank=True, editable=False, populate_from=["name"], verbose_name="slug"
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="type",
            field=models.CharField(
                choices=[("INT", "Internal"), ("EXT", "External")],
                default="INT",
                help_text="Internal groups are only visible to members, external groups are available via the API",
                max_length=3,
                verbose_name="type",
            ),
        ),
        migrations.AddField(
            model_name="teammembership",
            name="member",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="members.member",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teammembership",
            name="team",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="teams.team"
            ),
            preserve_default=False,
        ),
    ]
