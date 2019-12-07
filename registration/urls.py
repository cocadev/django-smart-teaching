"""lms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a UruRL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path,include
from . import views
import social_django
app_name = "registration"

urlpatterns = [
    path('login/', views.login_display, name='login'),
    path('register/', views.register_display, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/reset_password/', views.reset_password, name='reset'),
    url(r'display_reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        views.display_reset_password, name='display_reset_password'),
    path('course/', views.course_selection, name='course_selection'),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        views.activate, name='activate'),
    path('save_password/',views.save_password,name='save_password'),
    path('edit_profile/',views.editprofile,name='edit_profile'),
    path('all_profiles/',views.allprofiles,name='allprofiles'),
    path('professor/',views.professor,name='professor')
    ]
