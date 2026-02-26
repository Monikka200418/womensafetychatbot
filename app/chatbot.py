from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Intent:
    keywords: tuple[str, ...]
    response: str


INTENTS = (
    Intent(
        keywords=("sos", "help", "danger", "unsafe", "attack", "threat"),
        response=(
            "SOS Action Plan:\n"
            "1) Move to a crowded or lit place immediately.\n"
            "2) Call emergency helpline now: Police 100/112, Women Helpline 181, Ambulance 108.\n"
            "3) Use the Emergency page in this app to send an alert with your location.\n"
            "4) Keep your phone recording audio if possible."
        ),
    ),
    Intent(
        keywords=("live location", "location share", "share location", "gps"),
        response=(
            "Live Location Sharing (offline capable):\n"
            "- Open Safety Chatbot tools and tap 'Get Live Location'.\n"
            "- Save family contacts in Trusted Contacts.\n"
            "- Use 'Share SOS Update' to send location text via available apps."
        ),
    ),
    Intent(
        keywords=("record", "recording", "audio record", "auto record", "voice"),
        response=(
            "Auto Recording Support:\n"
            "- Tap 'Start Auto Recording' for emergency audio capture.\n"
            "- Use 'Panic Mode' to capture location and recording together.\n"
            "- Stop recording and share/download the file for evidence."
        ),
    ),
    Intent(
        keywords=("helpline", "number", "police", "ambulance", "emergency contact"),
        response=(
            "Emergency Numbers (offline quick list):\n"
            "- National Emergency: 112\n"
            "- Police: 100\n"
            "- Women Helpline: 181\n"
            "- Ambulance: 108\n"
            "- Cyber Crime: 1930"
        ),
    ),
    Intent(
        keywords=("travel", "cab", "taxi", "bus", "night", "route"),
        response=(
            "Safe Travel Checklist:\n"
            "- Share trip details with a trusted person before moving.\n"
            "- Verify vehicle number and driver before boarding.\n"
            "- Sit where exit is accessible and avoid isolated stops.\n"
            "- Keep emergency numbers on speed dial."
        ),
    ),
    Intent(
        keywords=("stalking", "harassment", "molest", "abuse", "violence"),
        response=(
            "If you face harassment:\n"
            "1) Move to safety first.\n"
            "2) Save evidence: screenshots, call logs, photos, date/time/location notes.\n"
            "3) Report to police or women helpline.\n"
            "4) Ask for legal support and a written complaint copy."
        ),
    ),
    Intent(
        keywords=("legal", "rights", "law", "complaint", "fir"),
        response=(
            "Legal Rights Quick Guide:\n"
            "- You can file an FIR at any police station.\n"
            "- You can request a woman officer for statement recording.\n"
            "- You are entitled to medical help and legal aid in emergencies.\n"
            "- Keep copies of all reports and case numbers."
        ),
    ),
    Intent(
        keywords=("self defense", "self-defence", "defense", "protect"),
        response=(
            "Self-Protection Basics:\n"
            "- Target vulnerable points only to create escape time.\n"
            "- Use loud voice commands to attract attention.\n"
            "- Carry legal safety tools where permitted.\n"
            "- Priority is escape, not confrontation."
        ),
    ),
    Intent(
        keywords=("mental", "stress", "anxiety", "panic", "scared"),
        response=(
            "Calm-Down Routine (60 seconds):\n"
            "- Inhale 4 seconds, hold 4 seconds, exhale 6 seconds.\n"
            "- Look around and name 5 things you can see.\n"
            "- Call a trusted contact and share your exact location."
        ),
    ),
)


DEFAULT_RESPONSE = (
    "I am your offline Women Safety Assistant.\n"
    "Ask me about: SOS, helpline numbers, safe travel, legal rights, harassment response, or self-defense."
)


def generate_offline_safety_reply(message: str) -> str:
    text = message.lower().strip()
    if not text:
        return DEFAULT_RESPONSE

    for intent in INTENTS:
        if any(keyword in text for keyword in intent.keywords):
            return intent.response

    return DEFAULT_RESPONSE
