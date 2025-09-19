# In LearningAPI/tests.py
from django.test import TestCase
from django.db import IntegrityError
from LearningAPI.models import Tag

class TagModelTest(TestCase):
    def setUp(self):
        Tag.objects.create(name="Django")
        Tag.objects.create(name="Python")

    def test_tag_string_representation(self):
        tag = Tag.objects.get(name="Django")
        self.assertEqual(str(tag), "Django")

    def test_tag_name_is_unique(self):
        # Verify uniqueness constraint
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Django")  # Duplicate name

# Create your tests here.
