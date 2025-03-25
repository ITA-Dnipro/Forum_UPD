import factory.django

from .models import CustomUser


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"test{n + 1}@test.com")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    password = factory.Faker("password")

    is_active = True

    @factory.post_generation
    def set_hashed_password(self, create, extracted, **kwargs):
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password(self.password)
        if create:
            self.save()
