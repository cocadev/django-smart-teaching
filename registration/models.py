from django.db import models
from django.contrib.auth.models import User



class course(models.Model):
    course_id = models.CharField(max_length=15,unique=True)
    course_name = models.CharField(max_length=100,unique=True)
    credits = models.IntegerField()

    def __str__(self):
        return course_name

class professor_profile(models.Model):
    professor = models.OneToOneField(User,on_delete=models.CASCADE)
    professor_description = models.CharField(max_length=150)
    professor_photo = models.ImageField(upload_to='media_/photos',default='media_/photos/download.png')
    professor_course = models.CharField(max_length=100)


# Create your models here.d
