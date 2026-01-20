from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from LearningAPI.models import Cohort, NSSUser
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
        self.nss_user = NSSUser.objects.create(
            user=self.user,
            slack_handle='@testinstructor',
            github_handle='testinstructor'
        )

        # Authenticate the test client
        self.client.force_authenticate(user=self.user)

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

    def test_list_cohorts_returns_200(self):
        """Test that GET /cohorts/ returns 200 OK."""
        # Arrange - done in setUp

        # Act - Make the HTTP request
        url = reverse('cohort-list')  # Using Django's reverse for URL
        response = self.client.get(url)

        # Assert - Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cohorts_returns_all_cohorts(self):
        """Test that GET /cohorts/ returns all cohorts in database."""
        # Act
        url = reverse('cohort-list')
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We created 2 cohorts

        # Verify data structure
        cohort_names = [cohort['name'] for cohort in response.data]
        self.assertIn("Test Cohort 1", cohort_names)
        self.assertIn("Test Cohort 2", cohort_names)

    def test_list_cohorts_unauthenticated_returns_401(self):
        """Test that unauthenticated request returns 401."""
        # Arrange - Remove authentication
        self.client.force_authenticate(user=None)

        # Act
        url = reverse('cohort-list')
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)