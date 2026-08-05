from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.urls import reverse
from LearningAPI.models import Cohort, NssUser
from datetime import date


class CohortEndpointTests(APITestCase):
    """Integration tests for Cohort API endpoints."""

    def setUp(self):
        """Create test fixtures and authenticate."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testinstructor',
            password='testpass123',
            is_staff=True
        )
        self.nss_user = NssUser.objects.create(
            user=self.user,
            slack_handle='@testinstructor',
            github_handle='testinstructor'
        )

        # Create token for the user
        self.token = Token.objects.create(user=self.user)

        # Authenticate using token (not force_authenticate)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create test cohorts
        self.cohort1 = Cohort.objects.create(
            name="Test Cohort 1",
            slack_channel="C12345",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            break_start_date=date(2024, 3, 15),
            break_end_date=date(2024, 3, 22),
            active=True
        )

        self.cohort2 = Cohort.objects.create(
            name="Test Cohort 2",
            slack_channel="C67890",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 12, 31),
            break_start_date=date(2024, 9, 15),
            break_end_date=date(2024, 9, 22),
            active=False
        )

    # Tests stay the same...
    def test_list_cohorts_returns_200(self):
        """Test that GET /cohorts/ returns 200 OK."""
        url = reverse('cohort-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cohorts_returns_all_cohorts(self):
        """Test that GET /cohorts/ returns all cohorts in database."""
        url = reverse('cohort-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        cohort_names = [cohort['name'] for cohort in response.data]
        self.assertIn("Test Cohort 1", cohort_names)
        self.assertIn("Test Cohort 2", cohort_names)

    def test_list_cohorts_unauthenticated_is_blocked(self):
        """Test that unauthenticated requests are blocked."""
        # Remove token authentication
        self.client.credentials()  # Clears the token

        url = reverse('cohort-list')
        response = self.client.get(url)

        # Should be blocked (not 200)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.status_code >= 400)