import random, string, json, valkey
import structlog

from django.conf import settings

from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from LearningAPI.models.people import StudentTeam, GroupProjectRepository, NSSUserTeam, Cohort
from LearningAPI.models.coursework import Project
from LearningAPI.utils import GithubRequest, SlackAPI

# Initialize structlog logger
logger = structlog.get_logger(__name__)


valkey_client = valkey.Valkey(
    host=settings.VALKEY_CONFIG['HOST'],
    port=settings.VALKEY_CONFIG['PORT'],
    db=settings.VALKEY_CONFIG['DB'],
)

class TeamRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupProjectRepository
        fields = ( 'id', 'project', 'repository' )


class StudentTeamSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    repositories = TeamRepoSerializer(many=True)

    def get_students(self, obj):
        return [{'id': student.id, 'name': student.name} for student in obj.students.all() if not student.user.is_staff]

    class Meta:
        model = StudentTeam
        fields = ( 'group_name', 'cohort', 'sprint_team', 'students', 'repositories' )


class TeamMakerView(ViewSet):
    """Team Maker"""
    def list(self, request):
        cohort_id=request.query_params.get('cohort', None)
        logger.info("list method called", cohort_id=cohort_id)

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            logger.info("Cohort retrieved successfully", cohort_id=cohort.id)

            teams = StudentTeam.objects.filter(cohort=cohort).order_by('-pk')
            logger.info("Teams retrieved successfully", team_count=teams.count())

            response = StudentTeamSerializer(teams, many=True).data
            logger.info("Returning successful response")
            return Response(response, status=status.HTTP_200_OK)
        except Cohort.DoesNotExist as ex:
            logger.error("Cohort not found", error=str(ex), cohort_id=cohort_id)
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """
        logger.info("create method called", cohort_id=request.data.get('cohort', None))

        cohort_id = request.data.get('cohort', None)
        student_list = request.data.get('students', None)
        group_project_id = request.data.get('groupProject', None)
        team_prefix = request.data.get('weeklyPrefix', None)

        issue_target_repos = []

        # Create the student team in the database
        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            logger.info("Cohort retrieved successfully", cohort_id=cohort.id)
        except Exception as ex:
            logger.error("Failed to get cohort", error=str(ex), cohort_id=cohort_id)
            return Response({'message': 'Invalid cohort ID'}, status=status.HTTP_400_BAD_REQUEST)

        team = StudentTeam()
        team.group_name = ""
        team.cohort = cohort
        team.sprint_team = group_project_id is not None
        logger.info("Creating new team", team_info={"cohort": cohort.id, "sprint_team": team.sprint_team})

        # Create the Slack channel and add students to it and store the channel ID in the team
        slack = SlackAPI()
        random_team_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        channel_name = f"{team_prefix}-{cohort.name.split(' ')[-1]}-{random_team_suffix}"
        channel_name = channel_name.lower()

        try:
            team.slack_channel = slack.create_channel(channel_name, student_list)
            logger.info("Slack channel created", channel=team.slack_channel)
        except Exception as ex:
            logger.error("Failed to create Slack channel", error=str(ex), channel_name=channel_name)
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        team.save()
        logger.info("Team saved successfully", team_id=team.id)

        # Assign the students to the team
        for student in student_list:
            student_team = NSSUserTeam()
            student_team.student_id = student
            student_team.team = team
            student_team.save()
            logger.info("Student added to team", student_id=student, team_id=team.id)

        # Create group project repository if group project is not None
        if group_project_id is not None:
            try:
                project = Project.objects.get(pk=group_project_id)
                logger.info("Project retrieved successfully", project_id=project.id)
            except Exception as ex:
                logger.error("Failed to get project", error=str(ex), project_id=group_project_id)
                return Response({'message': 'Invalid project ID'}, status=status.HTTP_400_BAD_REQUEST)

            # Get student Github organization name
            student_org_name = cohort.info.student_organization_url.split("/")[-1]
            logger.info("Student org name retrieved", org_name=student_org_name)

            # Create repositories
            for repo_type in ["client", "api"] if project.api_template_url else ["client"]:
                random_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
                repo_name = f'{project.name.replace(" ", "-")}-{repo_type}-{random_suffix}'
                logger.info(f"Creating {repo_type} repository", repo_name=repo_name)

                gh_request = GithubRequest()
                response = gh_request.create_repository(
                    source_url=getattr(project, f"{repo_type}_template_url"),
                    student_org_url=cohort.info.student_organization_url,
                    repo_name=repo_name,
                    project_name=project.name
                )

                if response.status_code != 201:
                    logger.error(f"Failed to create {repo_type} repository", status_code=response.status_code)
                    return Response({'message': f'Failed to create {repo_type} repository'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Grant write permissions
                for student in team.students.all(): # pylint: disable=E1101
                    gh_request.assign_student_permissions(
                        student_org_name=student_org_name,
                        repo_name=repo_name,
                        student=student
                    )
                    logger.info(f"Permissions granted for {repo_type} repository", student_id=student.id, repo_name=repo_name)

                # Save repository URL to database
                group_project_repo = GroupProjectRepository()
                group_project_repo.team_id = team.id
                group_project_repo.project = project
                group_project_repo.repository = f'https://github.com/{student_org_name}/{repo_name}'
                group_project_repo.save()
                logger.info(f"{repo_type.capitalize()} repository saved", repo_url=group_project_repo.repository)

                issue_target_repos.append(f'{student_org_name}/{repo_name}')

                # Send message to Slack
                created_repo_url = f'https://github.com/{student_org_name}/{repo_name}'
                slack.send_message(
                    text=f"🐙 Your {repo_type} repository has been created. Visit the URL below and clone the project to your machine.\n\n{created_repo_url}",
                    channel=team.slack_channel
                )
                logger.info(f"Slack message sent for {repo_type} repository", repo_url=created_repo_url)

            # Publish message to Redis
            message = json.dumps({
                'notification_channel': cohort.slack_channel,
                'source_repo': "/".join(project.client_template_url.split('/')[-2:]),
                'all_target_repositories': issue_target_repos
            })
            valkey_client.publish('channel_migrate_issue_tickets', message)
            logger.info("Published message to Redis", message=message)

        serialized_team = StudentTeamSerializer(team, many=False).data
        logger.info("Returning created team response", team_id=team.id)

        return Response(serialized_team, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def reset(self, request):
        logger.info("reset method called", cohort_id=request.query_params.get('cohort', None))

        cohort_id = request.query_params.get('cohort', None)

        if cohort_id is None:
            logger.warning("No cohort ID provided in reset request")
            return Response({'message': 'No cohort ID provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cohort = Cohort.objects.get(pk=cohort_id)
            logger.info("Cohort retrieved for deletion", cohort_id=cohort.id)

            self._delete_slack_channels(cohort)
            logger.info("Slack channels deleted for cohort", cohort_id=cohort.id)

            self._delete_cohort_teams(cohort)
            logger.info("Team data deleted for cohort", cohort_id=cohort.id)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Cohort.DoesNotExist as ex:
            logger.error("Cohort not found during reset", error=str(ex), cohort_id=cohort_id)
            return Response({'message': str(ex)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            logger.error("Error during reset operation", error=str(ex), cohort_id=cohort_id)
            return Response({'message': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _delete_cohort_teams(self, cohort):
        logger.info("_delete_cohort_teams called", cohort_id=cohort.id)
        NSSUserTeam.objects.filter(team__cohort=cohort).delete()
        GroupProjectRepository.objects.filter(team__cohort=cohort).delete()
        StudentTeam.objects.filter(cohort=cohort).delete()
        logger.info("All team data deleted for cohort", cohort_id=cohort.id)

    def _delete_slack_channels(self, cohort):
        logger.info("_delete_slack_channels called", cohort_id=cohort.id)
        current_teams = StudentTeam.objects.filter(cohort=cohort)

        for team in current_teams:
            slack = SlackAPI()
            slack.delete_channel(team.slack_channel)
            logger.info("Slack channel deleted", channel=team.slack_channel, team_id=team.id)

