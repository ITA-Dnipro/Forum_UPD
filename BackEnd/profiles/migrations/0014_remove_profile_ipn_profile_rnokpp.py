# Generated by Django 4.2.3 on 2024-04-17 14:51

from django.db import migrations, models
import validation.validate_rnokpp


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0013_alter_profile_regions"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="ipn",
        ),
        migrations.AddField(
            model_name="profile",
            name="rnokpp",
            field=models.CharField(
                blank=True,
                default=None,
                max_length=10,
                null=True,
                unique=True,
                validators=[validation.validate_rnokpp.validate_rnokpp],
            ),
        ),
    ]
