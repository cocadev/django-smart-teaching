from rest_framework import serializers
from dashboard.models import course_dashboard
from .models import User
class userlogserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')


class courselogserializer(serializers.ModelSerializer):
    professor = userlogserializer()
    class Meta:
        model = course_dashboard
        fields = (
            'professor',
            'course_difficulty',
            'course_average',
            'course',
            'needy_student_list',
            'course_student_list'
        )
