from django.db import models
from .nssuser_cohort import NssUserCohort

class Cohort(models.Model):
    """Model for student cohorts"""
    name = models.CharField(max_length=55, unique=True)
    slack_channel = models.CharField(max_length=55, unique=False)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    break_start_date = models.DateField(auto_now=False, auto_now_add=False)
    break_end_date = models.DateField(auto_now=False, auto_now_add=False)
    active = models.BooleanField(default=False)

    def __repr__(self) -> str:
        return f'{self.name}'

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def coaches(self):
        coaches = []
        user_cohorts = NssUserCohort.objects.filter(cohort=self, nss_user__user__is_staff=True)
        for user_cohort in user_cohorts:
            coaches.append({
                "id": user_cohort.nss_user.id,
                "name": f'{user_cohort.nss_user}'
            })
        return coaches

    @property
    def is_instructor(self):
        try:
            return self.__is_instructor
        except AttributeError:
            return False

    @is_instructor.setter
    def is_instructor(self, value):
        self.__is_instructor = value



    @property
    def students(self):
        """students property, which will be calculated per cohort

        Returns:
            int: Number of students per cohort
        """
        try:
            return self.__students
        except AttributeError:
            return 0

    @students.setter
    def students(self, value):
        self.__students = value

    def is_active_on_date(self, check_date):
        """
        Check if cohort is active on a given date.

        Args:
            check_date: A date object to check against cohort dates

        Returns:
            bool: True if check_date falls between start and end dates (inclusive),
                  False otherwise or if dates are not set
        """
        if not self.start_date or not self.end_date:
            return False
        return self.start_date <= check_date <= self.end_date
    