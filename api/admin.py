from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "name", "phone_number", "birthday", "gender", "preferred_language")
	search_fields = ("user__username", "user__email", "name")

