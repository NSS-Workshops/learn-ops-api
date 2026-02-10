from django.test import SimpleTestCase
from LearningAPI.models import Cohort

class DemoTests(SimpleTestCase):
# Hard to unit test (tightly coupled)
   def process_cohort(cohort_id):
       cohort = Cohort.objects.get(id=cohort_id)
       students = cohort.students.all()
       # ... complex logic mixed with database calls

   # Easier to unit test (logic separated)
   def calculate_cohort_completion_rate(total_students, completed_students):
       if total_students == 0:
           return 0
       return (completed_students / total_students) * 100