from django.urls import path
from . import views

app_name = 'student_report'

urlpatterns = [
    path('<int:id>/', views.student_report, name="student_report"),
    path('charts/<int:id>/', views.charts, name="charts"),
    path('tables/<int:id>/', views.tables, name="tables"),
]