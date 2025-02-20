from collections import defaultdict

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
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


class UserRegistrationSerializer(UserCreatePasswordRetypeSerializer):
    company = CustomProfileSerializer(write_only=True)
    email = serializers.EmailField(
        write_only=True,
    )
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    captcha = serializers.CharField(
        write_only=True, allow_blank=True, allow_null=True
    )

    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ("email", "password", "name", "surname", "company", "captcha")

    def validate(self, value):
        custom_errors = defaultdict(list)
        captcha_token = value.get("captcha")
        self.fields.pop("re_password", None)
        re_password = value.pop("re_password")
        email = value.get("email").lower()
        password = value.get("password")
        company_data = value.get("company")
        is_registered = company_data.get("is_registered")
        is_startup = company_data.get("is_startup")
        if User.objects.filter(email=email).exists():
            custom_errors["email"].append("Email is already registered")
        else:
            value["email"] = email
        if not is_registered and not is_startup:
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
        if value["password"] != re_password:
            custom_errors["password"].append("Passwords don't match.")
        if captcha_token and not verify_recaptcha(captcha_token):
            custom_errors["captcha"].append(
                "Invalid reCAPTCHA. Please try again."
            )
        if custom_errors:
            raise serializers.ValidationError(custom_errors)
        return value

    def create(self, validated_data):
        validated_data.pop("captcha", None)
        company_data = validated_data.pop("company")
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
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
