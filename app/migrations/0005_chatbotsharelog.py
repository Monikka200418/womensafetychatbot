from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_emergencyalert_audio_file_and_contacts_text"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatbotShareLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sender_name", models.CharField(default="Anonymous", max_length=100)),
                ("recipients", models.TextField(blank=True, default="")),
                ("share_type", models.CharField(default="text", max_length=20)),
                ("message", models.TextField(blank=True, default="")),
                ("location", models.CharField(blank=True, default="", max_length=300)),
                ("audio_file", models.FileField(blank=True, null=True, upload_to="chatbot_audio/")),
                ("video_file", models.FileField(blank=True, null=True, upload_to="chatbot_video/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
