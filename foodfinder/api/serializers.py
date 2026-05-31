from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FoodSearch, RestaurantResult


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password")

    def create(self, validated_data):
        user = User(username=validated_data.get("username"), email=validated_data.get("email", ""))
        user.set_password(validated_data["password"])
        user.save()
        return user


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


              
       
   
