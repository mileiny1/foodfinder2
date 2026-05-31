from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from .models import FoodSearch, RestaurantResult, UserProfile


class RegisteredUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="profile.name", read_only=True)
    home_address = serializers.CharField(source="profile.home_address", read_only=True)
    birthday = serializers.DateField(source="profile.birthday", read_only=True)
    phone_number = serializers.CharField(source="profile.phone_number", read_only=True)
    gender = serializers.CharField(source="profile.gender", read_only=True)
    preferred_language = serializers.CharField(source="profile.preferred_language", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "name",
            "home_address",
            "birthday",
            "phone_number",
            "gender",
            "preferred_language",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(write_only=True, max_length=255)
    home_address = serializers.CharField(write_only=True, allow_blank=True, required=False, max_length=500)
    birthday = serializers.DateField(write_only=True, required=False, allow_null=True)
    phone_number = serializers.CharField(write_only=True, allow_blank=True, required=False, max_length=25)
    gender = serializers.ChoiceField(write_only=True, choices=UserProfile.GENDER_CHOICES, required=False, default=UserProfile.GENDER_PREFER_NOT_TO_SAY)
    preferred_language = serializers.ChoiceField(
        write_only=True,
        choices=UserProfile.PREFERRED_LANGUAGE_CHOICES,
        required=False,
        default=UserProfile.LANGUAGE_ENGLISH,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password",
            "confirm_password",
            "name",
            "home_address",
            "birthday",
            "phone_number",
            "gender",
            "preferred_language",
        )
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def validate_email(self, value):
        normalized = (value or "").strip().lower()
        if not normalized:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized

    def _build_unique_username(self, email):
        base = (email.split("@", 1)[0] or "user").strip().replace(" ", "_")
        candidate = base
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base}_{suffix}"
            suffix += 1
        return candidate

    def create(self, validated_data):
        name = validated_data.pop("name")
        home_address = validated_data.pop("home_address", "")
        birthday = validated_data.pop("birthday", None)
        phone_number = validated_data.pop("phone_number", "")
        gender = validated_data.pop("gender", UserProfile.GENDER_PREFER_NOT_TO_SAY)
        preferred_language = validated_data.pop("preferred_language", UserProfile.LANGUAGE_ENGLISH)
        validated_data.pop("confirm_password", None)

        email = validated_data.get("email")
        username = (validated_data.get("username") or "").strip() or self._build_unique_username(email)

        user = User(username=username, email=email)
        user.set_password(validated_data["password"])
        user.save()

        UserProfile.objects.create(
            user=user,
            name=name,
            home_address=home_address,
            birthday=birthday,
            phone_number=phone_number,
            gender=gender,
            preferred_language=preferred_language,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "name",
            "home_address",
            "birthday",
            "phone_number",
            "gender",
            "preferred_language",
        )


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate(self, attrs):
        # Accept login payloads that provide either username or email.
        username = (attrs.get("username") or "").strip()
        email = (attrs.get("email") or "").strip()

        identifier = username or email
        if not identifier:
            raise serializers.ValidationError({"detail": "Provide username or email and password."})

        # If identifier is an email, resolve it to the internal username used by Django auth.
        if "@" in identifier:
            try:
                user = User.objects.get(email__iexact=identifier)
                attrs["username"] = user.username
            except User.DoesNotExist:
                # Keep a non-matching value so parent validation returns the standard auth error.
                attrs["username"] = identifier
        else:
            attrs["username"] = identifier
        
        data = super().validate(attrs)
        access_token = data.get("access")
        refresh_token = data.get("refresh")
        profile = getattr(self.user, "profile", None)

        # Keep default keys and add explicit aliases for frontend consumers.
        data["token"] = access_token
        data["access_token"] = access_token
        data["refresh_token"] = refresh_token
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "name": getattr(profile, "name", ""),
            "home_address": getattr(profile, "home_address", ""),
            "birthday": getattr(profile, "birthday", None),
            "phone_number": getattr(profile, "phone_number", ""),
            "gender": getattr(profile, "gender", UserProfile.GENDER_PREFER_NOT_TO_SAY),
            "preferred_language": getattr(profile, "preferred_language", UserProfile.LANGUAGE_ENGLISH),
        }
        return data


class RestaurantResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantResult
        fields = (
            "id",
            "name",
            "address",
            "lat",
            "lng",
            "distance_m",
            "rating",
            "price_level",
            "is_open_now",
            "provider_place_id",
            "provider",
        )


class FoodSearchSerializer(serializers.ModelSerializer):
    results = RestaurantResultSerializer(many=True, read_only=True)

    class Meta:
        model = FoodSearch
        fields = (
            "id",
            "user",
            "query",
            "user_lat",
            "user_lng",
            "provider",
            "expanded_terms",
            "filters",
            "created_at",
            "results",
        )


              
       
   
