from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings as django_settings
from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer,
    UserSerializer,
    TokenCreateSerializer,
)
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ratelimit.decorators import RateLimitDecorator
from ratelimit.exception import RateLimitException
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from profiles.models import Profile
from validation.validate_password import (
    validate_password_long,
    validate_password_include_symbols,
)
from validation.validate_profile import validate_profile
from validation.validate_recaptcha import verify_recaptcha

from validation.validate_password import validate_password_strength

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token


class CustomProfileSerializer(serializers.ModelSerializer):
    is_registered = serializers.BooleanField()
    is_startup = serializers.BooleanField()
    is_fop = serializers.BooleanField()

    class Meta:
        model = Profile
        fields = ("name", "is_registered", "is_startup", "is_fop")

class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "surname")


class UserRegistrationSerializer(serializers.ModelSerializer):
    company = CustomProfileSerializer(write_only=True)
    email = serializers.EmailField(
        required=True,
        write_only=True,
    )
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    re_password = serializers.CharField(write_only=True)
    captcha = serializers.CharField(
        write_only=True, allow_blank=True, allow_null=True
    )

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ("email", "password", "re_password", "name", "surname", "company", "captcha")

    def validate(self, value):
        custom_errors = defaultdict(list)
        captcha_token = value.get("captcha")
        self.fields.pop("re_password", None)
        re_password = value.get("re_password")
        email = value.get("email").lower()
        password = value.get("password")
        company_data = value.get("company")
        is_registered = company_data.get("is_registered")
        is_startup = company_data.get("is_startup")
        if User.objects.filter(email=email).exists():
            logger.error(f"Email is already registered {email}")
            custom_errors["email"].append("Email is already registered")
        else:
            value["email"] = email
        if not is_registered and not is_startup:
            logger.error("No recipient specified.")
            custom_errors["comp_status"].append(
                "Please choose who you represent."
            )
        try:
            validate_password_long(password)
        except ValidationError as error:
            custom_errors["password"].append(error.message)
        try:
            validate_password_include_symbols(password)
        except ValidationError as error:
            custom_errors["password"].append(error.message)
        try:
            validate_password_strength(password)
        except ValidationError as error:
            custom_errors["password"].append(error.message)
        if password != re_password:
            logger.error("Passwords don't match.")
            custom_errors["password"].append("Passwords don't match.")
        if captcha_token and not verify_recaptcha(captcha_token):
            logger.error("Invalid reCAPTCHA. Please try again.")
            custom_errors["captcha"].append(
                "Invalid reCAPTCHA. Please try again."
            )
        if custom_errors:
            logger.error(custom_errors)
            raise serializers.ValidationError(custom_errors)
        return value

    def create(self, validated_data):
        validated_data.pop("re_password", None)
        validated_data.pop("captcha", None)
        company_data = validated_data.pop("company")
        user = User.objects.create(
            email=validated_data["email"],
            name=validated_data["name"],
            surname=validated_data["surname"],
        )
        user.set_password(validated_data["password"])
        logger.info(f"Saving user {user.email}")
        user.save()
        Profile.objects.create(**company_data, person=user)
        return user


class UserListSerializer(UserSerializer):
    profile_id = serializers.PrimaryKeyRelatedField(
        source="profile", read_only=True
    )

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "name",
            "surname",
            "profile_id",
            "is_staff",
            "is_superuser",
        )


class CustomTokenCreateSerializer(TokenCreateSerializer):
    captcha = serializers.CharField(
        write_only=True, allow_blank=True, allow_null=True
    )

    def validate(self, attrs):
        captcha_token = attrs.get("captcha")

        try:
            validate_profile(attrs.get("email"))
        except ValidationError as error:
            raise serializers.ValidationError(error.message)

        try:
            return self.validate_for_rate(attrs)
        except RateLimitException:
            self.fail("inactive_account")

        if captcha_token and not verify_recaptcha(captcha_token):
            raise serializers.ValidationError(
                "Invalid reCAPTCHA. Please try again."
            )

    @RateLimitDecorator(
        calls=django_settings.ATTEMPTS_FOR_LOGIN,
        period=django_settings.DELAY_FOR_LOGIN,
    )
    def validate_for_rate(self, attrs):
        email = attrs.get(djoser_settings.LOGIN_FIELD).lower()
        new_attr = dict(
            [("password", attrs.get("password")), ("email", email)]
        )
        return super().validate(new_attr)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        request = self.context.get('request')
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.split()[1]
        refresh_token = data.get('refresh')

        try:
            decoded_access_token = AccessToken(access_token)
            user_id_from_access = decoded_access_token['user_id']
        except Exception as e:
            raise serializers.ValidationError({"access token error": str(e)})

        try:
            decoded_refresh_token = RefreshToken(refresh_token)
            user_id_from_refresh = decoded_refresh_token['user_id']
        except Exception as e:
            raise serializers.ValidationError({"refresh token error": str(e)})

        if user_id_from_access != user_id_from_refresh:
            raise serializers.ValidationError({"error": "User ID mismatch between tokens."})

        return data
