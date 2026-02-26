from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .chatbot import generate_offline_safety_reply
from .models import ChatbotShareLog, EmergencyAlert, TrustedContact


class ChatbotTests(TestCase):
    def test_chatbot_intent_for_sos(self):
        reply = generate_offline_safety_reply("I am in danger, need SOS now")
        self.assertIn("SOS Action Plan", reply)

    def test_chatbot_page_loads(self):
        response = self.client.get(reverse("chatbot"))
        self.assertEqual(response.status_code, 200)

    def test_chatbot_share_log_saved(self):
        audio = SimpleUploadedFile("clip.webm", b"fake-audio-content", content_type="audio/webm")
        response = self.client.post(
            reverse("chatbot_share_log"),
            {
                "sender_name": "jeni",
                "recipients": "9000000001,9000000002",
                "share_type": "audio",
                "message": "Emergency audio",
                "location": "12.9716,77.5946",
                "audio_file": audio,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatbotShareLog.objects.count(), 1)
        log = ChatbotShareLog.objects.first()
        self.assertEqual(log.sender_name, "jeni")
        self.assertEqual(log.share_type, "audio")


class AdminDeleteTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="pass12345",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.admin_user)

    def test_admin_can_delete_emergency_alert(self):
        alert = EmergencyAlert.objects.create(
            name="test",
            phone="9000000000",
            message="help",
            location="12.1,77.2",
        )
        response = self.client.post(reverse("delete_emergency_alert", args=[alert.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(EmergencyAlert.objects.filter(id=alert.id).exists())

    def test_admin_can_delete_chatbot_log(self):
        log = ChatbotShareLog.objects.create(
            sender_name="jeni",
            recipients="9000000000",
            share_type="text",
            message="SOS",
            location="12.1,77.2",
        )
        response = self.client.post(reverse("delete_chatbot_log", args=[log.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ChatbotShareLog.objects.filter(id=log.id).exists())

    def test_admin_can_run_cleanup(self):
        response = self.client.post(reverse("run_cleanup_now"), {"days": "30"})
        self.assertEqual(response.status_code, 302)


class TrustedContactsTests(TestCase):
    def test_save_and_load_trusted_contacts(self):
        response = self.client.post(
            reverse("trusted_contacts_save"),
            {"user_name": "jeni", "contacts": "9000000001,9000000002,9000000003"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrustedContact.objects.filter(user_name="jeni").count(), 3)

        load_response = self.client.get(reverse("trusted_contacts_load"), {"user_name": "jeni"})
        self.assertEqual(load_response.status_code, 200)
