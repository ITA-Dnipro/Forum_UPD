from collections import defaultdict

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings as django_settings

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
signer = TimestampSigner()


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

    class Meta:
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

class EmailActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email activation error.")
            logger.error("Email activation error.")
        if user.is_active:
            raise serializers.ValidationError("This account is already active.")
            logger.error("This account is already active.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.is_active = True
        user.save()

        return {'detail': 'Account successfully activated.'}


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer used for handling password reset requests.
    Validates email and generates reset token.
    """
    email = serializers.EmailField()

    def generate_new_token(self, user):
        return signer.sign(f"{user.pk}:{user.password}")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset process.
    Validates reset token and new password requirements.
    """
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        custom_errors = defaultdict(list)
        new_password = data["new_password"]

        try:
            validate_password_long(new_password)
        except ValidationError as error:
            custom_errors["new_password"].append(error.message)
        try:
            validate_password_include_symbols(new_password)
        except ValidationError as error:
            custom_errors["new_password"].append(error.message)
        try:
            validate_password_strength(new_password)
        except ValidationError as error:
            custom_errors["new_password"].append(error.message)

        try:
            decoded_uid_bytes = urlsafe_base64_decode(data["uid"])
            decoded_uid = force_str(decoded_uid_bytes)
        except Exception:
            raise serializers.ValidationError({"uid": "Invalid uid provided."})

        try:
            user = User.objects.get(pk=decoded_uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError(
                {"uid": "User does not exist. Please, try again."}
            )

        if user.check_password(new_password):
            custom_errors["new_password"].append("New password must be different from the current password.")

        if custom_errors:
            raise serializers.ValidationError(custom_errors)

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError({"token": "Token is invalid or expired"})

        return {"user": user, "new_password": new_password}

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password while authenticated.
    Validates old password and new password requirements.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        errors = []
        for validator in [
            validate_password_include_symbols,
            validate_password_strength,
            validate_password_long
        ]:
            try:
                validator(value)
            except ValidationError as error:
                errors.append(error.message)

        if errors:
            raise serializers.ValidationError({"new_password": errors})

        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if user.check_password(attrs["new_password"]):
            raise serializers.ValidationError(
                {"new_password": "New password must be different from the current password."})
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])