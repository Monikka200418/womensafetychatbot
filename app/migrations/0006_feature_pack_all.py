from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_chatbotsharelog"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatbotsharelog",
            name="evidence_hash",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="chatbotsharelog",
            name="location_history",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="chatbotsharelog",
            name="resolved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="chatbotsharelog",
            name="resolved_by",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="chatbotsharelog",
            name="status",
            field=models.CharField(default="new", max_length=20),
        ),
        migrations.AddField(
            model_name="emergencyalert",
            name="evidence_hash",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="emergencyalert",
            name="resolved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="emergencyalert",
            name="resolved_by",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="emergencyalert",
            name="status",
            field=models.CharField(default="new", max_length=20),
        ),
        migrations.CreateModel(
            name="AdminAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("admin_username", models.CharField(max_length=150)),
                ("action", models.CharField(max_length=100)),
                ("object_type", models.CharField(max_length=50)),
                ("object_id", models.IntegerField()),
                ("note", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="TrustedContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_name", models.CharField(max_length=100)),
                ("contact_name", models.CharField(blank=True, default="", max_length=100)),
                ("phone", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
