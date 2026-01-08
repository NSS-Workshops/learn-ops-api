"""
Integration tests for team_maker_view.py - Week 2 Day 2

This file demonstrates testing complex workflows with multiple external services.
Students will work in teams to expand these tests.

Key concepts:
- Using APITestCase for endpoint testing
- Mocking external services (GitHub, Slack, Valkey)
- Verifying integration behavior
- Testing error scenarios
"""
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock, ANY, call
from django.urls import reverse
from django.contrib.auth.models import User
from LearningAPI.models import (
    NSSUser, Cohort, StudentTeam, Project,
    CohortInfo, NSSUserCohort, GroupProjectRepository
)


class TeamMakerIntegrationTests(APITestCase):
    """
    Integration tests for the team maker endpoint.

    This tests the full workflow of creating teams including:
    - Database record creation
    - GitHub repository creation
    - Slack channel creation
    - Valkey message publishing
    """

    def setUp(self):
        """Create test fixtures for all integration tests."""
        # Create authenticated user (instructor)
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
        self.client.force_authenticate(user=self.user)

        # Create test cohort with required info
        self.cohort = Cohort.objects.create(
            name="Test Cohort 50",
            slack_channel="C12345",
            start_date="2024-01-01",
            end_date="2024-06-30",
            break_start_date="2024-03-15",
            break_end_date="2024-03-22",
            active=True
        )

        self.cohort_info = CohortInfo.objects.create(
            cohort=self.cohort,
            student_organization_url="https://github.com/test-org",
            client_course_url="https://example.com/client",
            server_course_url="https://example.com/server"
        )

        # Create test project
        self.project = Project.objects.create(
            name="Test Group Project",
            index=1,
            client_template_url="https://github.com/templates/client-template",
            api_template_url="https://github.com/templates/api-template",
            active=True
        )

        # Create test students
        self.student1_user = User.objects.create_user(
            username='student1',
            password='pass',
            is_staff=False
        )
        self.student1 = NSSUser.objects.create(
            user=self.student1_user,
            slack_handle='@student1',
            github_handle='student1gh'
        )

        self.student2_user = User.objects.create_user(
            username='student2',
            password='pass',
            is_staff=False
        )
        self.student2 = NSSUser.objects.create(
            user=self.student2_user,
            slack_handle='@student2',
            github_handle='student2gh'
        )

        # Enroll students in cohort
        NSSUserCohort.objects.create(nss_user=self.student1, cohort=self.cohort)
        NSSUserCohort.objects.create(nss_user=self.student2, cohort=self.cohort)

    @patch('LearningAPI.views.team_maker_view.valkey_client')
    @patch('LearningAPI.views.team_maker_view.GithubRequest')
    @patch('LearningAPI.views.team_maker_view.SlackAPI')
    def test_create_team_with_github_repos_success(self, MockSlack, MockGithub, mock_valkey):
        """
        INSTRUCTOR DEMO: Test successful team creation with all services.

        This demonstrates:
        1. Setting up multiple mocks
        2. Configuring mock return values
        3. Making the API request
        4. Verifying database changes
        5. Verifying external service calls
        """
        # Arrange: Configure mocks for external services
        # Mock Slack channel creation
        slack_instance = MockSlack.return_value
        slack_instance.create_channel.return_value = "C9876543"
        slack_instance.send_message.return_value = None

        # Mock GitHub repository creation
        github_instance = MockGithub.return_value
        github_instance.create_repository.return_value = MagicMock(
            status_code=201,
            json=lambda: {"html_url": "https://github.com/test-org/test-repo"}
        )
        github_instance.assign_student_permissions.return_value = None

        # Mock Valkey message publishing
        mock_valkey.publish = MagicMock(return_value=None)

        # Act: Make POST request to create team
        url = reverse('teammaker-list')
        data = {
            "cohort": self.cohort.id,
            "students": [self.student1.id, self.student2.id],
            "groupProject": self.project.id,
            "weeklyPrefix": "capstone"
        }
        response = self.client.post(url, data, format='json')

        # Assert: Verify response
        self.assertEqual(response.status_code, 201,
                        "Should return 201 Created on success")
        self.assertIn('group_name', response.data)
        self.assertIn('repositories', response.data)

        # Assert: Verify database changes
        self.assertEqual(StudentTeam.objects.count(), 1,
                        "Should create exactly one team")
        team = StudentTeam.objects.first()
        self.assertEqual(team.students.count(), 2,
                        "Team should have 2 students")
        self.assertEqual(team.cohort, self.cohort,
                        "Team should be in correct cohort")
        self.assertTrue(team.sprint_team,
                       "Team should be marked as sprint team")

        # Assert: Verify Slack was called correctly
        slack_instance.create_channel.assert_called_once()
        channel_name_arg = slack_instance.create_channel.call_args[0][0]
        self.assertIn('capstone', channel_name_arg.lower(),
                     "Channel name should include prefix")
        slack_instance.send_message.assert_called()

        # Assert: Verify GitHub was called correctly
        github_instance.create_repository.assert_called()
        # Should create both client and API repos
        self.assertEqual(github_instance.create_repository.call_count, 2,
                        "Should create both client and API repositories")

        # Verify student permissions were assigned
        github_instance.assign_student_permissions.assert_called()
        self.assertEqual(github_instance.assign_student_permissions.call_count, 4,
                        "Should assign permissions to both students for both repos")

        # Assert: Verify Valkey publish was called
        mock_valkey.publish.assert_called_once()
        publish_args = mock_valkey.publish.call_args[0]
        self.assertEqual(publish_args[0], 'channel_migrate_issue_tickets',
                        "Should publish to correct channel")

    @patch('LearningAPI.views.team_maker_view.valkey_client')
    @patch('LearningAPI.views.team_maker_view.GithubRequest')
    @patch('LearningAPI.views.team_maker_view.SlackAPI')
    def test_github_failure_returns_error(self, MockSlack, MockGithub, mock_valkey):
        """
        INSTRUCTOR DEMO: Test handling of GitHub API failure.

        This demonstrates:
        1. Simulating service failures with side_effect
        2. Verifying error response
        3. Checking that partial operations don't corrupt state
        """
        # Arrange: Mock Slack success but GitHub failure
        slack_instance = MockSlack.return_value
        slack_instance.create_channel.return_value = "C9876543"

        github_instance = MockGithub.return_value
        github_instance.create_repository.return_value = MagicMock(
            status_code=500  # Simulate GitHub API error
        )

        # Act: Attempt to create team
        url = reverse('teammaker-list')
        data = {
            "cohort": self.cohort.id,
            "students": [self.student1.id, self.student2.id],
            "groupProject": self.project.id,
            "weeklyPrefix": "capstone"
        }
        response = self.client.post(url, data, format='json')

        # Assert: Should return error status
        self.assertEqual(response.status_code, 500,
                        "Should return 500 on GitHub failure")
        self.assertIn('message', response.data,
                     "Error response should include message")

        # Assert: Team was still created (Slack succeeded)
        self.assertEqual(StudentTeam.objects.count(), 1,
                        "Team should still be created despite GitHub failure")

        # Assert: But no repositories were saved
        self.assertEqual(GroupProjectRepository.objects.count(), 0,
                        "No repository records should be saved on failure")

    @patch('LearningAPI.views.team_maker_view.valkey_client')
    @patch('LearningAPI.views.team_maker_view.GithubRequest')
    @patch('LearningAPI.views.team_maker_view.SlackAPI')
    def test_slack_failure_returns_error(self, MockSlack, MockGithub, mock_valkey):
        """
        TEST TEMPLATE for students: Test handling of Slack API failure.

        TODO: Students implement this test
        - Mock Slack to raise an exception
        - Verify 500 error response is returned
        - Check that no team is created if Slack fails
        """
        # Arrange
        slack_instance = MockSlack.return_value
        # TODO: Configure Slack to raise an exception

        # Act
        url = reverse('teammaker-list')
        data = {
            "cohort": self.cohort.id,
            "students": [self.student1.id, self.student2.id],
            "groupProject": self.project.id,
            "weeklyPrefix": "capstone"
        }
        # TODO: Make the POST request

        # Assert
        # TODO: Verify error response
        # TODO: Verify no team was created
        pass

    def test_missing_cohort_returns_error(self):
        """
        TEST TEMPLATE: Test that missing cohort ID returns appropriate error.

        TODO: Students implement this test
        - Don't include cohort in request data
        - Verify appropriate error response
        """
        pass

    def test_invalid_project_id_returns_error(self):
        """
        TEST TEMPLATE: Test that invalid project ID returns error.

        TODO: Students implement this test
        - Use non-existent project ID
        - Verify error handling
        """
        pass


class TeamMakerListTests(APITestCase):
    """
    Tests for listing existing teams (GET endpoint).

    TODO: Students can implement tests for the list() method.
    """

    def setUp(self):
        """Set up test fixtures."""
        # TODO: Create user, cohort, and teams for testing
        pass

    def test_list_teams_for_cohort(self):
        """
        TEST TEMPLATE: Test retrieving teams for a specific cohort.

        TODO: Students implement this test
        """
        pass

    def test_list_teams_without_cohort_parameter(self):
        """
        TEST TEMPLATE: Test listing teams without cohort filter.

        TODO: Students decide how this should behave and test it
        """
        pass


class TeamMakerResetTests(APITestCase):
    """
    Tests for the reset endpoint (DELETE).

    TODO: Students can implement tests for the reset() method.
    """

    def setUp(self):
        """Set up test fixtures."""
        pass

    @patch('LearningAPI.views.team_maker_view.SlackAPI')
    def test_reset_deletes_teams_and_slack_channels(self, MockSlack):
        """
        TEST TEMPLATE: Test that reset properly cleans up teams and Slack.

        TODO: Students implement this test
        - Create teams
        - Call reset endpoint
        - Verify teams are deleted
        - Verify Slack API was called to delete channels
        """
        pass


# ============================================================================
# STUDENT TEAM ASSIGNMENTS
# ============================================================================

# Team 1: Focus on successful GitHub repo creation workflow
#   - Expand test_create_team_with_github_repos_success
#   - Add test for creating team without group project
#   - Add test for verifying repo naming conventions
#   - Add test for verifying permissions are set correctly

# Team 2: Focus on GitHub error handling and retry logic
#   - Implement test_slack_failure_returns_error
#   - Add test for GitHub timeout scenarios
#   - Add test for partial success (one repo succeeds, one fails)
#   - Add test for GitHub rate limiting

# Team 3: Focus on team member management (adding collaborators to repos)
#   - Add test for verifying all students get added to repos
#   - Add test for handling students with invalid GitHub handles
#   - Add test for adding students to existing teams
#   - Add test for removing students from teams

# Team 4: Focus on integration between GitHub + Slack (both services)
#   - Add test verifying Slack message includes repo URL
#   - Add test for coordinating failures between services
#   - Add test for message formatting in Slack
#   - Add test for Slack notifications on repo creation

# Team 5: Focus on data validation before external API calls
#   - Implement test_missing_cohort_returns_error
#   - Implement test_invalid_project_id_returns_error
#   - Add test for empty student list
#   - Add test for invalid student IDs
#   - Add test for missing required fields

# Team 6: Focus on edge cases (empty teams, invalid data, etc.)
#   - Add test for duplicate team creation
#   - Add test for special characters in team names
#   - Add test for very long team names
#   - Add test for teams with only one student
#   - Add test for teams with many students (> 10)