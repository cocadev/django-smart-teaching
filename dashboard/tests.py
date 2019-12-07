from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from .models import Enrollments
from .views import dashboard, needy_list

class TestDetails(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Enrollments.objects.create(course_id='5', student_id='6',student_name='gupta', prof_id='3',status="wefwe",performance="wefw",persistance="we",label="iwebf")

    def test_str_string_matches(self):
        enrollment = Enrollments.objects.get(id=1)
        expected_str_return = "gupta"
        self.assertEqual(expected_str_return, enrollment.student_name)


# class TestUrls(SimpleTestCase):
#     def test_dashboard(self):
#         url = reverse('dashboard')
#
#         self.assertEquals(resolve(url).func.view_class, dashboard)