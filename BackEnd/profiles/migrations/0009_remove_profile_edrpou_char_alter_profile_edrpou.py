# Generated by Django 4.2.3 on 2024-02-06 19:21

from django.db import migrations, models
import validation.validate_edrpou


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0008_profile_edrpou_char"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="edrpou_char",
        ),
        migrations.AlterField(
            model_name="profile",
            name="edrpou",
            field=models.CharField(
                default=None,
                max_length=8,
                null=True,
                unique=True,
                validators=[validation.validate_edrpou.validate_edrpou],
            ),
        ),
    ]
