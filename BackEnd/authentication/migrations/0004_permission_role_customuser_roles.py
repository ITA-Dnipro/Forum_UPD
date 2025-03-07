# Generated by Django 4.2.3 on 2025-03-04 22:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_auto_20250204_1656"),
    ]

    operations = [
        migrations.CreateModel(
            name="Permission",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("codename", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Role",
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
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "permissions",
                    models.ManyToManyField(
                        blank=True, related_name="roles", to="authentication.permission"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="customuser",
            name="roles",
            field=models.ManyToManyField(
                blank=True, related_name="users", to="authentication.role"
            ),
        ),
    ]
