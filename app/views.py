import base64
import csv
import hashlib
import random
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .chatbot import generate_offline_safety_reply
from .models import AdminAuditLog, ChatbotShareLog, EmergencyAlert, Register, TrustedContact


def _calc_file_hash(file_field):
    if not file_field:
        return ""
    hasher = hashlib.sha256()
    file_field.open("rb")
    try:
        for chunk in file_field.chunks():
            hasher.update(chunk)
    finally:
        file_field.close()
    return hasher.hexdigest()


def _audit(request, action, object_type, object_id, note=""):
    if request.user.is_authenticated:
        AdminAuditLog.objects.create(
            admin_username=request.user.username,
            action=action,
            object_type=object_type,
            object_id=object_id,
            note=note,
        )


def _run_cleanup(days=30):
    threshold = timezone.now() - timedelta(days=days)
    old_alerts = EmergencyAlert.objects.filter(created_at__lt=threshold)
    old_logs = ChatbotShareLog.objects.filter(created_at__lt=threshold)
    alert_count = old_alerts.count()
    log_count = old_logs.count()
    for alert in old_alerts:
        if alert.audio_file:
            alert.audio_file.delete(save=False)
    for log in old_logs:
        if log.audio_file:
            log.audio_file.delete(save=False)
        if log.video_file:
            log.video_file.delete(save=False)
    old_alerts.delete()
    old_logs.delete()
    return alert_count, log_count


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def register(request):
    if request.method == "POST":
        obj = Register()
        obj.name = request.POST.get("name")
        obj.number = request.POST.get("no")
        obj.email = request.POST.get("email")
        obj.password = make_password(request.POST.get("pwd", ""))
        obj.dt = request.POST.get("date")
        obj.save()
        return redirect("login")
    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        password = request.POST.get("pwd", "").strip()
        otp = request.POST.get("otp", "").strip()

        if otp:
            expected_otp = request.session.get("login_otp")
            pending_user = request.session.get("pending_login_user")
            if otp == expected_otp and pending_user:
                request.session["name"] = pending_user
                request.session.pop("login_otp", None)
                request.session.pop("pending_login_user", None)
                return redirect("home")
            messages.error(request, "Invalid OTP")
            return render(request, "login.html", {"otp_required": True, "name": pending_user or name})

        try:
            re = Register.objects.get(name=name)
        except Register.DoesNotExist:
            return HttpResponse("Invalid user")
        valid_password = check_password(password, re.password) if re.password.startswith("pbkdf2_") else (re.password == password)
        if valid_password:
            if not re.password.startswith("pbkdf2_"):
                re.password = make_password(password)
                re.save(update_fields=["password"])
            generated_otp = str(random.randint(100000, 999999))
            request.session["login_otp"] = generated_otp
            request.session["pending_login_user"] = name
            messages.info(request, f"OTP: {generated_otp}")
            return render(request, "login.html", {"otp_required": True, "name": name})
        return HttpResponse("Invalid password")
    return render(request, "login.html", {"otp_required": False})


def table(request):
    da = Register.objects.all()
    return render(request, "table.html", {"reg": da})


def delete(request, id):
    r = Register.objects.get(id=id)
    r.delete()
    return redirect("table")


def update(request, id):
    r = Register.objects.get(id=id)
    return render(request, "update.html", {"data": r})


def update_new(request, id):
    if request.method == "POST":
        obj = Register.objects.get(id=id)
        obj.name = request.POST.get("name")
        obj.number = request.POST.get("no")
        obj.email = request.POST.get("email")
        new_pw = request.POST.get("pwd")
        if new_pw:
            obj.password = make_password(new_pw)
        obj.save()
        return redirect("table")
    return redirect("table")


def emergency(request):
    if request.method == "POST":
        audio_upload = request.FILES.get("audio_file")
        alert = EmergencyAlert.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            location=request.POST.get("location"),
            message=request.POST.get("message"),
            contacts_text=request.POST.get("contacts_text", "").strip(),
            audio_file=audio_upload,
        )

        audio_data = request.POST.get("audio_data", "").strip()
        if audio_data and not audio_upload and "," in audio_data:
            header, encoded = audio_data.split(",", 1)
            ext = "webm"
            if "audio/wav" in header:
                ext = "wav"
            elif "audio/mp4" in header:
                ext = "m4a"
            try:
                decoded_audio = base64.b64decode(encoded)
                filename = f"sos_{uuid.uuid4().hex}.{ext}"
                alert.audio_file.save(filename, ContentFile(decoded_audio), save=True)
            except Exception:
                pass

        alert.evidence_hash = _calc_file_hash(alert.audio_file)
        alert.save(update_fields=["evidence_hash"])
        return redirect("home")

    return render(request, "emergency.html")


def is_admin(user):
    return user.is_superuser


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            messages.success(request, "Admin login successful")
            return redirect("admin_dashboard")
        messages.error(request, "Invalid Admin Credentials")
    return render(request, "admin_login.html")


def _apply_filters(queryset, request, prefix=""):
    q = request.GET.get(f"{prefix}q", "").strip()
    status = request.GET.get(f"{prefix}status", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()
    if q:
        if hasattr(queryset.model, "sender_name"):
            queryset = queryset.filter(
                Q(message__icontains=q) | Q(location__icontains=q) | Q(recipients__icontains=q) | Q(sender_name__icontains=q)
            )
        else:
            queryset = queryset.filter(
                Q(message__icontains=q) | Q(location__icontains=q) | Q(contacts_text__icontains=q) | Q(name__icontains=q)
            )
    if status:
        queryset = queryset.filter(status=status)
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    return queryset


def _export_csv(filename, headers, rows):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response


def _export_pdf(text_lines, filename):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return HttpResponse("PDF library missing. Install reportlab.", status=501)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    c = canvas.Canvas(response, pagesize=A4)
    y = 800
    for line in text_lines:
        c.drawString(40, y, str(line)[:130])
        y -= 16
        if y <= 40:
            c.showPage()
            y = 800
    c.save()
    return response


@login_required
@user_passes_test(is_admin)
def emergency_table(request):
    alerts = EmergencyAlert.objects.all().order_by("-created_at")
    chatbot_logs = ChatbotShareLog.objects.all().order_by("-created_at")

    # Bulk actions.
    if request.method == "POST":
        action = request.POST.get("bulk_action", "").strip()
        alert_ids = request.POST.getlist("selected_alerts")
        log_ids = request.POST.getlist("selected_logs")
        now = timezone.now()
        if action == "delete":
            for alert in EmergencyAlert.objects.filter(id__in=alert_ids):
                if alert.audio_file:
                    alert.audio_file.delete(save=False)
                _audit(request, "delete", "EmergencyAlert", alert.id)
                alert.delete()
            for log in ChatbotShareLog.objects.filter(id__in=log_ids):
                if log.audio_file:
                    log.audio_file.delete(save=False)
                if log.video_file:
                    log.video_file.delete(save=False)
                _audit(request, "delete", "ChatbotShareLog", log.id)
                log.delete()
        elif action in {"in_progress", "resolved"}:
            EmergencyAlert.objects.filter(id__in=alert_ids).update(
                status=action,
                resolved_by=request.user.username if action == "resolved" else "",
                resolved_at=now if action == "resolved" else None,
            )
            ChatbotShareLog.objects.filter(id__in=log_ids).update(
                status=action,
                resolved_by=request.user.username if action == "resolved" else "",
                resolved_at=now if action == "resolved" else None,
            )
        return redirect("emergency_table")

    # Filters.
    alerts = _apply_filters(alerts, request, prefix="a_")
    chatbot_logs = _apply_filters(chatbot_logs, request, prefix="c_")
    c_type = request.GET.get("c_type", "").strip()
    if c_type:
        chatbot_logs = chatbot_logs.filter(share_type=c_type)

    # Exports.
    export = request.GET.get("export", "").strip()
    if export == "csv_alerts":
        return _export_csv(
            "emergency_alerts.csv",
            ["id", "name", "phone", "contacts", "location", "message", "status", "created_at"],
            [
                [a.id, a.name, a.phone, a.contacts_text, a.location, a.message, a.status, a.created_at]
                for a in alerts
            ],
        )
    if export == "csv_chatbot":
        return _export_csv(
            "chatbot_logs.csv",
            ["id", "sender", "recipients", "type", "location", "message", "status", "created_at"],
            [
                [c.id, c.sender_name, c.recipients, c.share_type, c.location, c.message, c.status, c.created_at]
                for c in chatbot_logs
            ],
        )
    if export == "pdf":
        lines = ["Women Safety Incident Report", "Emergency Alerts"]
        lines += [f"{a.id} | {a.name} | {a.location} | {a.status}" for a in alerts[:100]]
        lines += ["", "Chatbot Logs"]
        lines += [f"{c.id} | {c.sender_name} | {c.share_type} | {c.location} | {c.status}" for c in chatbot_logs[:100]]
        return _export_pdf(lines, "incident_report.pdf")

    alerts.filter(is_seen=False).update(is_seen=True)
    _audit(request, "view", "EmergencyTable", 0, note="Opened emergency-table page")
    return render(
        request,
        "emergency_table.html",
        {
            "alerts": alerts,
            "chatbot_logs": chatbot_logs,
        },
    )


@require_POST
@login_required
@user_passes_test(is_admin)
def delete_emergency_alert(request, alert_id):
    alert = get_object_or_404(EmergencyAlert, id=alert_id)
    if alert.audio_file:
        alert.audio_file.delete(save=False)
    _audit(request, "delete", "EmergencyAlert", alert.id)
    alert.delete()
    return redirect("emergency_table")


@require_POST
@login_required
@user_passes_test(is_admin)
def delete_chatbot_log(request, log_id):
    log = get_object_or_404(ChatbotShareLog, id=log_id)
    if log.audio_file:
        log.audio_file.delete(save=False)
    if log.video_file:
        log.video_file.delete(save=False)
    _audit(request, "delete", "ChatbotShareLog", log.id)
    log.delete()
    return redirect("emergency_table")


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    new_alerts = EmergencyAlert.objects.filter(is_seen=False).count()
    return render(request, "admin_dashboard.html", {"new_alerts": new_alerts})


@login_required
@user_passes_test(is_admin)
def incident_timeline(request):
    combined = []
    for a in EmergencyAlert.objects.all().order_by("-created_at")[:200]:
        combined.append({
            "created_at": a.created_at,
            "event_type": "Emergency Alert",
            "title": a.name,
            "details": f"{a.location} | {a.message}",
            "status": a.status,
        })
    for c in ChatbotShareLog.objects.all().order_by("-created_at")[:200]:
        combined.append({
            "created_at": c.created_at,
            "event_type": f"Chatbot {c.share_type}",
            "title": c.sender_name,
            "details": f"{c.location} | {c.message}",
            "status": c.status,
        })
    combined.sort(key=lambda x: x["created_at"], reverse=True)
    _audit(request, "view", "IncidentTimeline", 0, note="Opened timeline")
    return render(request, "incident_timeline.html", {"events": combined})


@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    logs = AdminAuditLog.objects.all().order_by("-created_at")[:500]
    return render(request, "audit_logs.html", {"logs": logs})


@require_POST
@login_required
@user_passes_test(is_admin)
def run_cleanup_now(request):
    days = int(request.POST.get("days", "30") or "30")
    alert_count, log_count = _run_cleanup(days=days)
    messages.success(request, f"Cleanup done: removed {alert_count} alerts and {log_count} chatbot logs older than {days} days.")
    _audit(request, "cleanup", "Records", 0, note=f"days={days}")
    return redirect("admin_dashboard")


def chatbot(request):
    if request.GET.get("clear") == "1":
        request.session["chat_history"] = []
        return redirect("chatbot")

    history = request.session.get("chat_history", [])
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            reply = generate_offline_safety_reply(message)
            history.append({"user": message, "bot": reply})
            request.session["chat_history"] = history[-20:]
            request.session.modified = True
    return render(
        request,
        "chatbot.html",
        {"history": request.session.get("chat_history", []), "sender_name": request.session.get("name", "Anonymous")},
    )


@require_POST
def chatbot_share_log(request):
    sender_name = request.POST.get("sender_name", "").strip() or request.session.get("name", "Anonymous")
    recipients = request.POST.get("recipients", "").strip()
    share_type = request.POST.get("share_type", "text").strip() or "text"
    message = request.POST.get("message", "").strip()
    location = request.POST.get("location", "").strip()
    location_history = request.POST.get("location_history", "").strip()

    log = ChatbotShareLog.objects.create(
        sender_name=sender_name,
        recipients=recipients,
        share_type=share_type,
        message=message,
        location=location,
        location_history=location_history,
        audio_file=request.FILES.get("audio_file"),
        video_file=request.FILES.get("video_file"),
    )
    source_file = log.audio_file or log.video_file
    log.evidence_hash = _calc_file_hash(source_file)
    log.save(update_fields=["evidence_hash"])
    return JsonResponse({"ok": True, "id": log.id})


@require_POST
def trusted_contacts_save(request):
    user_name = request.POST.get("user_name", "").strip() or request.session.get("name", "Anonymous")
    raw_contacts = request.POST.get("contacts", "")
    parsed = [x.strip() for x in raw_contacts.split(",") if x.strip()]
    TrustedContact.objects.filter(user_name=user_name).delete()
    for phone in parsed[:3]:
        TrustedContact.objects.create(user_name=user_name, phone=phone)
    return JsonResponse({"ok": True, "count": len(parsed[:3])})


def trusted_contacts_load(request):
    user_name = request.GET.get("user_name", "").strip() or request.session.get("name", "Anonymous")
    contacts = list(TrustedContact.objects.filter(user_name=user_name).order_by("id").values_list("phone", flat=True)[:3])
    return JsonResponse({"ok": True, "contacts": contacts})
