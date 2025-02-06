from django.db import migrations
from faker import Faker
import random

def seed_data(apps, schema_editor):
    fake = Faker('uk_UA')
    Category = apps.get_model('profiles', 'Category')
    Activity = apps.get_model('profiles', 'Activity')
    Region = apps.get_model('profiles', 'Region')
    Profile = apps.get_model('profiles', 'Profile')
    CustomUser = apps.get_model('authentication', 'CustomUser')

    # Categories
    categories_ukr = [
        "Технології", "Мистецтво", "Мода", "Соціальні проекти",
        "Освіта", "Медицина", "Спорт", "Туризм",
        "Кулінарія", "Музика", "Кіно", "Література",
        "Наука", "Екологія", "Фінанси", "Будівництво",
        "Автомобілі", "Ігри", "Подорожі", "Фотографія",
        "Психологія", "Фітнес", "Журналістика", "Релігія",
        "Політика", "Історія", "Філософія", "Маркетинг",
        "Дизайн інтер'єру", "Ювелірна справа", "Косметологія", "Військова справа"
    ]

    existing_categories = set(Category.objects.values_list('name', flat=True))
    new_categories = [Category(name=cat) for cat in categories_ukr if cat not in existing_categories]
    Category.objects.bulk_create(new_categories)

    # Activities
    activities_ukr = [
        "Програмування", "Дизайн", "Сільське господарство", "Торгівля",
        "Викладання", "Лікування", "Тренерство", "Екскурсії",
        "Готування", "Виконання музики", "Зйомка фільмів", "Написання книг",
        "Дослідження", "Захист природи", "Банківська справа", "Ремонт",
        "Автосервіс", "Розробка ігор", "Організація подорожей", "Фотозйомка",
        "Консультування", "Тренування", "Написання статей", "Проведення обрядів",
        "Політична діяльність", "Вивчення історії", "Викладання філософії", "Реклама",
        "Оформлення інтер'єру", "Виготовлення прикрас", "Догляд за шкірою", "Військова служба"
    ]

    existing_activities = set(Activity.objects.values_list('name', flat=True))
    new_activities = [Activity(name=act) for act in activities_ukr if act not in existing_activities]
    Activity.objects.bulk_create(new_activities)

    # Regions
    regions_ukr = [
        ("Київська", "Kyiv"),
        ("Львівська", "Lviv"),
        ("Одеська", "Odesa"),
        ("Харківська", "Kharkiv"),
        ("Донецька", "Donetsk"),
        ("Дніпропетровська", "Dnipropetrovsk"),
        ("Івано-Франківська", "Ivano-Frankivsk"),
        ("Запорізька", "Zaporizhzhia"),
        ("Вінницька", "Vinnytsia"),
        ("Житомирська", "Zhytomyr"),
        ("Полтавська", "Poltava"),
        ("Рівненська", "Rivne"),
        ("Сумська", "Sumy"),
        ("Тернопільська", "Ternopil"),
        ("Херсонська", "Kherson"),
        ("Хмельницька", "Khmelnytskyi"),
        ("Черкаська", "Cherkasy"),
        ("Чернівецька", "Chernivtsi"),
        ("Чернігівська", "Chernihiv"),
        ("Закарпатська", "Zakarpattia"),
        ("Миколаївська", "Mykolaiv"),
        ("Кіровоградська", "Kropyvnytskyi"),
        ("Волинська", "Volyn"),
        ("Луганська", "Luhansk"),
        ("АР Крим", "Crimea")
    ]

    existing_regions = set(Region.objects.values_list('name_ukr', flat=True))
    new_regions = [
        Region(name_eng=eng_name, name_ukr=ukr_name)
        for ukr_name, eng_name in regions_ukr
        if ukr_name not in existing_regions
    ]
    Region.objects.bulk_create(new_regions)

    # Profiles

    startup_users = list(CustomUser.objects.filter(email__in=[f"user{i}@gmail.com" for i in range(1,21)]))
    investor_users = list(CustomUser.objects.filter(email__in=[f"user{i}@gmail.com" for i in range(21,31)]))

    existing_profile_user_ids = set(Profile.objects.filter(
        person__in=startup_users + investor_users
    ).values_list('person_id', flat=True))

    profiles_to_create = []

    # Cтартапи
    for user in startup_users:
        if user.id not in existing_profile_user_ids:
            profiles_to_create.append(Profile(
                person=user,
                name=fake.company(),
                is_registered=True,
                is_startup=True,
                official_name=f"ТОВ '{fake.company_suffix()}'",
                common_info=fake.text(max_nb_chars=200),
                address=f"{fake.city()}, {fake.street_address()}",
                startup_idea=fake.catch_phrase(),
                founded=random.randint(2010, 2024),
            ))

    # Інвестори
    for user in investor_users:
        if user.id not in existing_profile_user_ids:
            profiles_to_create.append(Profile(
                person=user,
                name=fake.name(),
                is_registered=True,
                is_startup=False,
                official_name=f"ФОП '{fake.last_name()}'",
                common_info=fake.text(max_nb_chars=200),
                address=f"{fake.city()}, {fake.street_address()}",
            ))

    # Створюємо усі профілі(стартапи\інвестори)
    Profile.objects.bulk_create(profiles_to_create)

class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0022_alter_profile_name_alter_profile_official_name"),
        ("authentication", "0003_auto_20250204_1656"), 
    ]

    operations = [
        migrations.RunPython(seed_data),
    ]

