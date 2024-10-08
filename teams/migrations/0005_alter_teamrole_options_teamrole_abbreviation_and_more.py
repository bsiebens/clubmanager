# Generated by Django 5.0.7 on 2024-08-14 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0004_alter_numberpool_options_numberpool_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="teamrole",
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "team role",
                "verbose_name_plural": "team roles",
            },
        ),
        migrations.AddField(
            model_name="teamrole",
            name="abbreviation",
            field=models.CharField(
                default="test",
                help_text="Abbreviated version of the name",
                max_length=10,
                unique=True,
                verbose_name="abbreviation",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teamrole",
            name="admin_role",
            field=models.BooleanField(
                default=False,
                help_text="Admin roles can manage the team (add/remove members, post messages, create events)",
                verbose_name="admin",
            ),
        ),
        migrations.AddField(
            model_name="teamrole",
            name="name",
            field=models.CharField(
                default="test", max_length=250, unique=True, verbose_name="name"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="teamrole",
            name="sort_order",
            field=models.IntegerField(
                default=100,
                help_text="By adjusting the sort order this role will displayed higher on the team page, by default roles are sorted by order (low to high) and then alphabetically",
                verbose_name="sort order",
            ),
        ),
        migrations.AddField(
            model_name="teamrole",
            name="staff_role",
            field=models.BooleanField(
                default=False,
                help_text="Staff roles are displayed on the team page under the staff section",
                verbose_name="staff",
            ),
        ),
    ]
