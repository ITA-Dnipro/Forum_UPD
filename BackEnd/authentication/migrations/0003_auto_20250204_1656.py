from django.db import migrations
from faker import Faker
from django.contrib.auth.hashers import make_password

def create_users(apps, schema_editor):
    fake = Faker('uk_UA')

    CustomUser = apps.get_model('authentication', 'CustomUser')
    
    if not CustomUser.objects.filter(email='admin@gmail.com').exists():
        admin_user = CustomUser(
            email='admin@gmail.com',
            name='AdminName',
            surname='AdminSurname',
            is_active=True,
            is_staff=True,
            is_superuser=True,
            password=make_password('admin12345'),
        )
        admin_user.save()
    
    for i in range(1, 31):
        email = f'user{i}@gmail.com'
        if not CustomUser.objects.filter(email=email).exists():
            
            name = (fake.unique.first_name_male() if i % 2 == 0 
                    else fake.unique.first_name_female())
            surname = (fake.unique.last_name_male() if i % 2 == 0 
                       else fake.unique.last_name_female())
            
            user = CustomUser(
                email=email,
                name=name,
                surname=surname,
                is_active=True,
                password=make_password('user12345'),
            )
            user.save()

def remove_users(apps, schema_editor):
    CustomUser = apps.get_model('authentication', 'CustomUser')
    CustomUser.objects.filter(email='admin@gmail.com').delete()
    for i in range(1, 31):
        email = f'user{i}@gmail.com'
        CustomUser.objects.filter(email=email).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0002_alter_customuser_email"),
    ]

    operations = [
        migrations.RunPython(create_users, remove_users),
    ]