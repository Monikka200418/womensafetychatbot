from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_emergencyalert_is_seen_alter_emergencyalert_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="emergencyalert",
            name="audio_file",
            field=models.FileField(blank=True, null=True, upload_to="emergency_audio/"),
        ),
        migrations.AddField(
            model_name="emergencyalert",
            name="contacts_text",
            field=models.TextField(blank=True, default=""),
        ),
    ]
