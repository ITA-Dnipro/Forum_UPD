# Generated by Django 4.2.3 on 2024-06-14 09:45
import os
from hashlib import md5

from PIL import Image
from django.db import migrations


def get_image_md5(image):
    with Image.open(image) as img:
        hash_md5 = md5(img.tobytes()).hexdigest()
    return hash_md5


def move_image_fields_to_profile_image_model(app, schema_editor):
        Profile = app.get_model("profiles", "Profile")
        ProfileImage = app.get_model("images", "ProfileImage")
        for instance in Profile.objects.all():
            if instance.banner_image and not instance.banner_approved:
                image_filename = instance.banner_image.name.split("/")[-1]
                image_instance = ProfileImage.objects.create(
                    image_path=os.path.join("banner", image_filename),
                    image_type="banner",
                    image_size = instance.banner_image.size,
                    content_type = image_filename.split(".")[-1],
                    hash_md5=get_image_md5(instance.banner_image),
                    created_by=instance.person,
                    is_approved=True,
                )
                instance.banner_approved = image_instance
                instance.save()
            if instance.logo_image and not instance.logo_approved:
                image_filename = instance.logo_image.name.split("/")[-1]
                image_instance = ProfileImage.objects.create(
                    image_path=os.path.join("logo", image_filename),
                    image_type="logo",
                    image_size = instance.logo_image.size,
                    content_type = image_filename.split(".")[-1],
                    hash_md5=get_image_md5(instance.logo_image),
                    created_by=instance.person,
                    is_approved=True,
                )
                instance.logo_approved = image_instance
                instance.save()


def update_completeness_value(app, schema_editor):
        Profile = app.get_model("profiles", "Profile")
        Region = app.get_model("profiles", "Region")
        Activity = app.get_model("profiles", "Activity")
        Category = app.get_model("profiles", "Category")
        for instance in Profile.objects.all():
            instance.completeness = 0
            if instance.banner_approved:
                instance.completeness += 100
            if instance.logo_approved:
                instance.completeness += 1
            if Activity.objects.all().filter(profile=instance.id):
                instance.completeness += 1
            if Category.objects.all().filter(profile=instance.id):
                instance.completeness += 1
            if Region.objects.all().filter(profile=instance.id):
                instance.completeness += 1
            instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ("images", "0001_initial"),
        (
            "profiles",
            "0015_profile_banner_profile_banner_approved_profile_logo_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(move_image_fields_to_profile_image_model, migrations.RunPython.noop, elidable=True),
        migrations.RunPython(update_completeness_value, reverse_code=migrations.RunPython.noop, elidable=True),
    ]
