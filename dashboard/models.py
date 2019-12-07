from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Enrollments(models.Model):
    course_id = models.CharField(max_length=15)
    student_id = models.CharField(max_length=15)
    student_name = models.CharField(max_length=60)
    prof_id = models.CharField(max_length=15)
    status = models.CharField(max_length=20)
    performance = models.CharField(max_length=20,default='-')
    persistance = models.CharField(max_length=20,default='-')
    label = models.CharField(max_length=90,default='-')


    def __str__(self):
        return self.student_name

class csvfile(models.Model):
    req_file = models.FileField(upload_to='media_')

class Marks(models.Model):
    student_name = models.CharField(max_length=15)
    student_id = models.CharField(default=0,max_length=15)
    course_id = models.CharField(default=0,max_length=15)
    prof_id = models.CharField(default=0,max_length=15)
    marks = models.FloatField(default=0)
    q_name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('student_id', 'course_id','prof_id','q_name','student_name')

class student_ranks(models.Model):
    student_id = models.CharField(max_length=15)
    course = models.CharField(max_length=50,default='-')
    class_rank = models.IntegerField(default=0)
    exam_rank = models.IntegerField(default=0)
    lab_rank = models.IntegerField(default=0)
    asgn_rank = models.IntegerField(default=0)
    oth_rank = models.IntegerField(default=0)
    best_marks = models.IntegerField(default=0)
    worst_marks = models.IntegerField(default=0)
    best_exam  = models.CharField(max_length=50,default='-')
    worst_exam = models.CharField(max_length=50, default='-')
    overall  = models.IntegerField(default=0)

class course_dashboard(models.Model):
    professor = models.OneToOneField(User,on_delete=models.CASCADE)
    course = models.CharField(max_length=50,default='-')
    course_difficulty = models.CharField(max_length=15,default='-')
    course_risk = models.CharField(max_length=15,default='-')
    course_average = models.CharField(max_length=15,default='-')
    exam_difficulty = models.CharField(max_length=15,default='-')
    exam_cheat_risk = models.CharField(max_length=15,default='-')
    exam_average = models.CharField(max_length=15,default='-')
    quartile_1 = models.FloatField(default=0)
    quartile_2 = models.FloatField(default=0)
    quartile_3 = models.FloatField(default=0)
    course_student_list = models.CharField(max_length=150,default='-')
    exam_student_list = models.CharField(max_length=150,default='-')
    needy_student_list = models.CharField(max_length=150,default='-')

class course_exams(models.Model):
    course_id = models.CharField(max_length=150,default='-')
    quiz_name = models.CharField(max_length=150,default='-')
    max_marks = models.IntegerField(default=0)
    avg_marks = models.CharField(max_length=50,default=0)