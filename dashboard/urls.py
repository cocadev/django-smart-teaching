from django.urls import path
from . import views
from registration import views as p

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('needy_list/', views.needy_list, name='needy_list'),
    path('list_of_students/', views.list_of_students, name='list_of_students'),
    path('editprofile/', p.editprofile, name='editprofile'),
    path('custom_404/', views.custom_404, name='custom_404'),
    path('graph', views.graph, name='graph'),
]
