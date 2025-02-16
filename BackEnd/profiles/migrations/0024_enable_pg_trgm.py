from django.db import migrations, connection


def enable_pg_trgm(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


class Migration(migrations.Migration):
    dependencies = [
        (
            "profiles", "0023_auto_20250204_1656",
        ),  # Update this with the latest migration dependency
    ]

    operations = [
        migrations.RunPython(enable_pg_trgm),
    ]
