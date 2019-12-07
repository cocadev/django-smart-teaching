from django.test import TestCase
from django.test import SimpleTestCase

from django.urls import reverse, resolve
from .forms import LoginForm
from .models import course
from django.contrib.auth.models import User
from .views import login_display, save_password, logout, allprofiles, course_selection

# Create your tests here.



# class TestUrls(SimpleTestCase):
#
#     def test_login_display_url_is_resolved(self):
#         url = reverse('login')
#         self.assertEquals(resolve(url).func, login_display)


class LoginFormTest(TestCase):

    emailVar = 'srg9504@gmail.com'
    passwordVar = '12345'


    def test_check_if_already_exists(self):
        form = LoginForm(data={'emailid':self.emailVar, 'password':self.passwordVar})

        self.assertFalse(form.is_valid())
        #self.assertTrue(form.is_valid())



    def test_check_if_does_not_exists(self):
        self.emailVar = 'avbdca@gmail.com'
        self.passwordVar = 'jaslncwaevl'

        form = LoginForm(data={'emailid': self.emailVar, 'password': self.passwordVar})

        self.assertFalse(form.is_valid())


    # def test_check_if_registered_exists(self):
    #     self.emailVar = 'srg9504@gmail.com'
    #     self.passwordVar = '12345'
    #
    #     User.objects.create(email=self.emailVar, password=self.passwordVar)
    #
    #     form = LoginForm(data={'emailid': self.emailVar, 'password': self.passwordVar})
    #
    #     self.assertFalse(form.is_valid())

class CourseModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        course.objects.create(course_name='Mathematics',course_id=54,credits=6)



    def test_check_str_of_model(self):

        current_course = course.objects.get(course_id=54)
        expected_name = 'Mathematics'
        self.assertTrue(course.course_name, 'Mathematics')
