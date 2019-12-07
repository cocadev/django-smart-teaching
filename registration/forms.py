from django import forms
from .models import professor_profile, course
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .passCheck import check_pass

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}))
    email = forms.EmailField(max_length=100,
                             widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}))
    first_name = forms.CharField(max_length=100,
                                 widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',}))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )

    def clean_email(self):

        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        email_qset = User.objects.filter(email=email)

        if email_qset.exists():
            raise forms.ValidationError('Email is taken already')
        return email

    def clean_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")

        user_qset = User.objects.filter(username=username)

        if user_qset.exists():
            raise forms.ValidationError('User name is taken already')
        return username

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords did not match')
            return confirm_password
        error=check_pass(str(password),str(cleaned_data['email']),str(cleaned_data['username']))
        print(error)
        if error:
            raise forms.ValidationError(error)
        return confirm_password


class LoginForm(forms.Form):
    emailid = forms.EmailField(
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': "input100", 'placeholder': 'Email Id'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "input100", 'placeholder': 'Password'}))

    def clean_emailid(self):
        cleaned_data = super().clean()
        emailid = cleaned_data.get("emailid")
        email_set = User.objects.filter(email=emailid)

        if not email_set.exists():
            raise forms.ValidationError('Email is not registered')
        else:
            user = User.objects.get(email=emailid)
            if not user.is_active:
                raise forms.ValidationError('User not authenticated')
        return emailid

    def clean_password(self):
        cleaned_data = super().clean()
        emailid = cleaned_data.get("emailid")
        email_set = User.objects.filter(email=emailid)

        if email_set.exists():
            password = cleaned_data.get('password')
            user = User.objects.get(email=emailid)
            userlog = authenticate(username=user, password=password)
            if userlog is None:
                raise forms.ValidationError('Invalid password')
            return password


class ProfileForm(forms.ModelForm):
    professor_description = forms.CharField(max_length=200, widget=forms.Textarea())
    professor_course = forms.CharField()
    professor_photo = forms.ImageField()

    class Meta:
        model = professor_profile
        fields = ('professor_description',
                  'professor_photo', 'professor_course')

    def clean_professor_description(self):
        cleaned_data = super().clean()
        professor_description = cleaned_data.get('professor_description')
        return professor_description

    def clean_professor_course(self):
        cleaned_data = super().clean()
        professor_course = str(cleaned_data.get('professor_course'))
        professor_course = professor_course.upper()
        courselist = course.objects.filter(course_id=professor_course)
        if not courselist.exists():
            raise forms.ValidationError('course does not exist')
        return professor_course


class ResetForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': "form-control"}))

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_set = User.objects.filter(email=email)

        if not email_set.exists():
            raise forms.ValidationError('Email is not registered')
        return email


class CourseForm(forms.Form):
    course_id = forms.CharField()

    def clean_course_id(self):
        cleaned_data = super().clean()
        course_id = str(cleaned_data.get('course_id'))
        course_id = course_id.upper()
        courselist = course.objects.filter(course_id=course_id)
        if not courselist.exists():
            raise forms.ValidationError('course does not exist')
        return course_id


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError('Passwords did not match')
        return confirm_password
