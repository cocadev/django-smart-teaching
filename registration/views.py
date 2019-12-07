from django.shortcuts import render, redirect
from .models import professor_profile, User
from django.core.mail import send_mail
from django.shortcuts import HttpResponse
from .forms import RegisterForm, LoginForm, ResetForm, ProfileForm, CourseForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .forms import ResetPasswordForm
from dashboard.models import course_dashboard
from .models import course
from .serailizer import courselogserializer
from rest_framework.response import Response
from rest_framework.decorators import api_view


# login

def login_display(request):
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        if form.is_valid():
            emailid = form.cleaned_data.get("emailid")
            password = form.cleaned_data.get('password')
            print(emailid)
            userlog = User.objects.get(email=emailid)
            print(userlog)
            user = authenticate(username=userlog, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect('dashboard:dashboard')
                else:
                    return HttpResponse('Not registered')
    else:
        form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'login/login.html', context)


# register


def register_display(request):
    if (request.method == 'POST'):
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data["username"],
                                            email=form.cleaned_data["email"],
                                            password=form.cleaned_data["password"]
                                            )

            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.is_active = False
            user.save()
            professor_profile.objects.create(professor=user)
            course_dashboard.objects.create(professor=user)
            mail = form.cleaned_data.get('email')
            print(mail)
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('login/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })

            send_mail(mail_subject, message, 'iiits2021@gmail.com', [mail])
            return render(request, 'login/email_confirmation.html')

    else:
        form = RegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'login/register1.html', context)


'''

logout

'''


@login_required
def logout_view(request):
    logout(request)
    return redirect('registration:login')


'''

forgot password

'''


def reset_password(request):
    if request.method == 'POST':
        form1 = ResetForm(request.POST)
        if form1.is_valid():
            mail = form1.cleaned_data.get('email')
            user = User.objects.get(email=mail)
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Link.'
            message = render_to_string('login/reset_confirm_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })

            send_mail(mail_subject, message, 'iiits2021@gmail.com', [mail])
            return render(request, 'login/reset_email.html', {'form': form1,'message':'Email has been sent to '+mail})
    else:
        form1 = ResetForm()
    return render(request, 'login/reset_email.html', {'form': form1,'message':''})


def display_reset_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # login(request, user)
        request.session['email'] = user.email
        return redirect('registration:save_password')

    else:
        return HttpResponse('Activation link is invalid!')


def save_password(request):
    if request.method == "POST":
        form1 = ResetPasswordForm(request.POST)
        if form1.is_valid():
            mail = request.session['email']
            user = User.objects.get(email=mail)
            print(user)
            user.set_password(form1.cleaned_data.get('new_password'))
            user.save()
            return HttpResponse(
                "Password has been reset Please login<a href='{{ url 'registrartion:login' }}'>here</a>")
    else:
        form1 = ResetPasswordForm()
    return render(request, 'login/reset_password.html', {'form': form1})


def editprofile(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        print(user)
        form1 = ProfileForm(request.POST, request.FILES, instance=professor_profile.objects.get(professor=user))
        if form1.is_valid():
            profile = form1.save(commit=False)
            profile.professor_description = form1.cleaned_data['professor_description']
            profile.professor_course = form1.cleaned_data['professor_course']
            profile.save()
            return redirect('dashboard:dashboard')

    else:
        user = User.objects.get(username=request.user)
        profile = professor_profile.objects.get(professor=user)
        form1 = ProfileForm(initial={'professor_description': profile.professor_description,
                                    'professor_photo': profile.professor_photo,
                                    'professor_course': profile.professor_course})

    return render(request, 'login/profile.html', {'form': form1})


def allprofiles(request):
    professors_details = []
    users = User.objects.all()
    for i in users:
        if not i.is_superuser:
            professor = User.objects.get(username=i)
            profile = professor_profile.objects.get(professor=professor)
            details = (
            str(professor.first_name + ' ' + professor.last_name), profile.professor_photo, profile.professor_course,
            profile.professor_description,i)
            professors_details.append(details)
    return render(request, 'login/all_profiles.html', {'professor_details': professors_details})


def show_profile(request):
    user1 = User.objects.get(username=request.user)
    profile1 = professor_profile.objects.get(professor=user1)
    return render(request, 'login/show_profile.html', {'user': user1, 'profile': profile1})


#@login_required()
def course_selection(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        profile = professor_profile.objects.get(professor=user)
        profile.professor_course = str(request.POST.get('radio'))
        profile.save()
        return redirect('dashboard:dashboard')
    else:
        courselist = course.objects.all()
        courseList = []
        for i in courselist:
            courseList.append([i.course_id, i.course_name, i.credits])
    return render(request, 'login/course.html', {'courseList': courseList})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('registration:course_selection')

    else:
        return HttpResponse('Activation link is invalid!')


@api_view()
def courselogdetail(request,course_id):
    course = course_dashboard.objects.filter(course=str(course_id).upper())
    serializer1 = courselogserializer(course,many=True)
    return Response(serializer1.data)

def professor(request):
    user = User.objects.get(username=request.user)
    profile = professor_profile.objects.get(professor=user)
    return render(request,'login/user_profie.html',{'name':user.first_name+' '+user.last_name,'photo':profile.professor_photo
                                                    ,'description':profile.professor_description,'userid':user.username,
                                                    'email':user.email,'coursename':profile.professor_course})
