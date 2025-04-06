from django.db import models

from django.contrib.auth.models import User

class ClassSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=50)
    discussion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course_name} - {self.user.username}"
