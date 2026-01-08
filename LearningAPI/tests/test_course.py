"""
Unit tests for Course model methods - Group 1 Assignment

TODO: Implement tests for the is_prerequisite_for() method.

Your team should test:
1. This course comes before other course (returns True)
2. This course comes after other course (returns False)
3. Same course (returns False)
4. Missing index on either course (handle gracefully)
5. Any other edge cases you discover

Remember:
- Use SimpleTestCase (no database needed)
- Follow the AAA pattern (Arrange-Act-Assert)
- Write descriptive test names
- Include docstrings explaining what each test does
"""
from django.test import SimpleTestCase
from LearningAPI.models.coursework import Course


class CourseMethodTests(SimpleTestCase):
    """
    Unit tests for Course.is_prerequisite_for() method.
    """

    def test_is_prerequisite_when_course_comes_before(self):
        """
        TODO: Test that is_prerequisite_for returns True when
        this course's index is less than the other course's index.
        """
        # Arrange
        # TODO: Create two course instances with appropriate indices

        # Act
        # TODO: Call is_prerequisite_for on the first course

        # Assert
        # TODO: Assert the result is True
        pass

    def test_is_prerequisite_when_course_comes_after(self):
        """
        TODO: Test that is_prerequisite_for returns False when
        this course's index is greater than the other course's index.
        """
        pass

    # TODO: Add more test methods for other scenarios