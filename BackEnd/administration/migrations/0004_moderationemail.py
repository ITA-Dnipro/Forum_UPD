# Generated by Django 4.2.3 on 2024-09-01 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0003_autoapprovetask"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModerationEmail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "email_moderation",
                    models.EmailField(max_length=254, unique=True),
                ),
            ],
        ),
    ]
