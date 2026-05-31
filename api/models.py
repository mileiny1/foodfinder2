from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDER_PREFER_NOT_TO_SAY = "prefer_not_to_say"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
        (GENDER_PREFER_NOT_TO_SAY, "Prefer not to say"),
    ]

    LANGUAGE_ENGLISH = "en"
    LANGUAGE_SPANISH = "es"
    LANGUAGE_FRENCH = "fr"
    LANGUAGE_PORTUGUESE = "pt"
    PREFERRED_LANGUAGE_CHOICES = [
        (LANGUAGE_ENGLISH, "English"),
        (LANGUAGE_SPANISH, "Spanish"),
        (LANGUAGE_FRENCH, "French"),
        (LANGUAGE_PORTUGUESE, "Portuguese"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255)
    home_address = models.CharField(max_length=500, blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=25, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=GENDER_PREFER_NOT_TO_SAY)
    preferred_language = models.CharField(max_length=8, choices=PREFERRED_LANGUAGE_CHOICES, default=LANGUAGE_ENGLISH)

    def __str__(self):
        return f"Profile<{self.user_id}>"


class FoodSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_searches')
    query = models.CharField(max_length=200)
    user_lat = models.FloatField()
    user_lng = models.FloatField()

    provider = models.CharField(max_length=20)
    expanded_terms = models.JSONField(default=list)
    filters = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}:{self.query}"


class RestaurantResult(models.Model):
    search = models.ForeignKey(FoodSearch, on_delete=models.CASCADE, related_name='results')
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True)


    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    distance_m = models.FloatField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    is_open_now = models.BooleanField(null=True, blank=True)
    provider_place_id = models.CharField(max_length=200, blank=True)
    provider = models.CharField(max_length=20, default="unknown") 

    def __str__(self):
        return self.name
    

