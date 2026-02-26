from django.db import models

# Create your models here.
class Register(models.Model):
    name=models.CharField(max_length=30)
    number=models.CharField(max_length=30)
    email=models.EmailField()
    password=models.CharField(max_length=30)
    dt=models.DateField()

    def __str__(self):
        return self.name
class EmergencyAlert(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    message = models.TextField()
    location = models.CharField(max_length=200)
    contacts_text = models.TextField(blank=True, default="")
    audio_file = models.FileField(upload_to="emergency_audio/", blank=True, null=True)
    evidence_hash = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, default="new")
    resolved_by = models.CharField(max_length=100, blank=True, default="")
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)


    def __str__(self):
        return self.name


class ChatbotShareLog(models.Model):
    sender_name = models.CharField(max_length=100, default="Anonymous")
    recipients = models.TextField(blank=True, default="")
    share_type = models.CharField(max_length=20, default="text")
    message = models.TextField(blank=True, default="")
    location = models.CharField(max_length=300, blank=True, default="")
    location_history = models.TextField(blank=True, default="")
    audio_file = models.FileField(upload_to="chatbot_audio/", blank=True, null=True)
    video_file = models.FileField(upload_to="chatbot_video/", blank=True, null=True)
    evidence_hash = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(max_length=20, default="new")
    resolved_by = models.CharField(max_length=100, blank=True, default="")
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_name} - {self.share_type}"


class TrustedContact(models.Model):
    user_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.phone}"


class AdminAuditLog(models.Model):
    admin_username = models.CharField(max_length=150)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.IntegerField()
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_username} {self.action} {self.object_type}:{self.object_id}"
