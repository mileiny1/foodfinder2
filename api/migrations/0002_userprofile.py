from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("home_address", models.CharField(blank=True, max_length=500)),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                            ("prefer_not_to_say", "Prefer not to say"),
                        ],
                        default="prefer_not_to_say",
                        max_length=20,
                    ),
                ),
                (
                    "preferred_language",
                    models.CharField(
                        choices=[
                            ("en", "English"),
                            ("es", "Spanish"),
                            ("fr", "French"),
                            ("pt", "Portuguese"),
                        ],
                        default="en",
                        max_length=8,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
