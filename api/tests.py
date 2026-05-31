from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserProfile


class RegisterApiTests(APITestCase):
	def test_register_creates_user_with_profile_fields(self):
		payload = {
			"email": "newuser@example.com",
			"password": "securepass123",
			"confirm_password": "securepass123",
			"name": "New User",
			"home_address": "123 Main St",
			"birthday": "1996-07-20",
			"phone_number": "+1 555 101 2020",
			"gender": UserProfile.GENDER_FEMALE,
			"preferred_language": UserProfile.LANGUAGE_SPANISH,
		}

		response = self.client.post("/api/auth/register/", payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["email"], payload["email"])
		self.assertEqual(response.data["name"], payload["name"])
		self.assertEqual(response.data["home_address"], payload["home_address"])
		self.assertEqual(response.data["birthday"], payload["birthday"])
		self.assertEqual(response.data["phone_number"], payload["phone_number"])
		self.assertEqual(response.data["gender"], payload["gender"])
		self.assertEqual(response.data["preferred_language"], payload["preferred_language"])

		user = User.objects.get(email=payload["email"])
		self.assertTrue(hasattr(user, "profile"))
		self.assertEqual(user.profile.name, payload["name"])
		self.assertEqual(str(user.profile.birthday), payload["birthday"])
		self.assertEqual(user.profile.phone_number, payload["phone_number"])

	def test_register_rejects_password_mismatch(self):
		payload = {
			"email": "mismatch@example.com",
			"password": "securepass123",
			"confirm_password": "differentpass123",
			"name": "Mismatch User",
		}

		response = self.client.post("/api/auth/register/", payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("confirm_password", response.data)

	def test_register_options_returns_dropdown_choices(self):
		response = self.client.get("/api/auth/register/options/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("gender", response.data)
		self.assertIn("preferred_language", response.data)
		self.assertIn("field_meta", response.data)
		self.assertEqual(response.data["field_meta"]["birthday"]["type"], "date")
		self.assertTrue(any(item["value"] == UserProfile.GENDER_MALE for item in response.data["gender"]))
		self.assertTrue(
			any(
				item["value"] == UserProfile.LANGUAGE_ENGLISH
				for item in response.data["preferred_language"]
			)
		)


class LoginApiTests(APITestCase):
	def setUp(self):
		"""Create a test user for login tests"""
		payload = {
			"email": "login@example.com",
			"password": "testpass123",
			"confirm_password": "testpass123",
			"name": "Login Test User",
		}
		self.client.post("/api/auth/register/", payload, format="json")

	def test_login_with_email(self):
		"""Test that users can login with email"""
		response = self.client.post("/api/auth/login/", {
			"username": "login@example.com",
			"password": "testpass123",
		}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access_token", response.data)
		self.assertIn("refresh_token", response.data)
		self.assertIn("user", response.data)
		self.assertEqual(response.data["user"]["email"], "login@example.com")

	def test_login_with_wrong_password(self):
		"""Test that login fails with wrong password"""
		response = self.client.post("/api/auth/login/", {
			"username": "login@example.com",
			"password": "wrongpassword",
		}, format="json")

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_login_with_nonexistent_email(self):
		"""Test that login fails with non-existent email"""
		response = self.client.post("/api/auth/login/", {
			"username": "nonexistent@example.com",
			"password": "testpass123",
		}, format="json")

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileApiTests(APITestCase):
	def setUp(self):
		payload = {
			"email": "profile@example.com",
			"password": "testpass123",
			"confirm_password": "testpass123",
			"name": "Profile User",
		}
		self.client.post("/api/auth/register/", payload, format="json")
		login_response = self.client.post(
			"/api/auth/login/",
			{
				"username": payload["email"],
				"password": payload["password"],
			},
			format="json",
		)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access_token']}")

	def test_patch_profile_updates_preferred_language(self):
		response = self.client.patch(
			"/api/auth/profile/",
			{"preferred_language": UserProfile.LANGUAGE_FRENCH},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["preferred_language"], UserProfile.LANGUAGE_FRENCH)

		user = User.objects.get(email="profile@example.com")
		self.assertEqual(user.profile.preferred_language, UserProfile.LANGUAGE_FRENCH)
		

