# api/models.py
from django.db import models
from django.contrib.auth.models import User

class TeacherApprovalRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


class PDFFile(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/pdfs/')
    description = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class VideoFile(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/videos/')
    description = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AssignmentFile(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/assignments/')
    description = models.TextField(blank=True, null=True)
    class_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ActivityLog(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50)
    class_name = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

