"""
Unit tests for Cohort model methods.

This demonstrates testing model methods without database access using SimpleTestCase.
Students will follow this pattern to test other models.
"""
from django.test import SimpleTestCase
from datetime import date
from LearningAPI.models import Cohort


class CohortMethodTests(SimpleTestCase):
    """
    Unit tests for Cohort model methods.
    Using SimpleTestCase because we test logic, not database.
    """

    def test_is_active_on_date_within_range(self):
        """
        Test that is_active_on_date returns True when check_date falls
        within the cohort's start and end dates.
        """
        # Arrange: Create a cohort with start and end dates
        cohort = Cohort(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )
        check_date = date(2024, 3, 15)  # Mid-point date

        # Act: Check if cohort is active on this date
        result = cohort.is_active_on_date(check_date)

        # Assert: Should return True since date is in range
        self.assertTrue(result, "Cohort should be active on date within range")

    def test_is_active_on_date_before_start(self):
        """
        Test that is_active_on_date returns False when check_date is
        before the cohort's start date.
        """
        # Arrange
        cohort = Cohort(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )
        check_date = date(2023, 12, 31)  # Day before start

        # Act
        result = cohort.is_active_on_date(check_date)

        # Assert
        self.assertFalse(result, "Cohort should not be active before start date")

    def test_is_active_on_date_after_end(self):
        """
        Test that is_active_on_date returns False when check_date is
        after the cohort's end date.
        """
        # Arrange
        cohort = Cohort(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )
        check_date = date(2024, 7, 1)  # Day after end

        # Act
        result = cohort.is_active_on_date(check_date)

        # Assert
        self.assertFalse(result, "Cohort should not be active after end date")

    def test_is_active_on_date_missing_dates(self):
        """
        Test that is_active_on_date returns False when cohort has
        missing start or end dates.
        """
        # Arrange: Cohort with None for dates
        cohort = Cohort(start_date=None, end_date=None)
        check_date = date(2024, 3, 15)

        # Act
        result = cohort.is_active_on_date(check_date)

        # Assert
        self.assertFalse(result, "Cohort without dates should not be active")

    def test_is_active_on_start_date(self):
        """
        Test that is_active_on_date returns True on the cohort's
        exact start date (boundary condition).
        """
        # Arrange
        cohort = Cohort(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )
        check_date = date(2024, 1, 1)  # Exact start date

        # Act
        result = cohort.is_active_on_date(check_date)

        # Assert
        self.assertTrue(result, "Cohort should be active on its start date")

    def test_is_active_on_end_date(self):
        """
        Test that is_active_on_date returns True on the cohort's
        exact end date (boundary condition).
        """
        # Arrange
        cohort = Cohort(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )
        check_date = date(2024, 6, 30)  # Exact end date

        # Act
        result = cohort.is_active_on_date(check_date)

        # Assert
        self.assertTrue(result, "Cohort should be active on its end date")