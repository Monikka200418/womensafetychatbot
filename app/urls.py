from django.urls import path
from . import views



urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"), 
    path("about/", views.about, name="about"),  # Keep only one
    path("register/", views.register, name="register"),
    path("emergency/", views.emergency, name="emergency"),
    path("table/", views.table, name="table"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("update/<int:id>/", views.update, name="update"),
    path("update_new/<int:id>/", views.update_new, name="update_new"),
    path('emergency-table/', views.emergency_table, name='emergency_table'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/share-log/', views.chatbot_share_log, name='chatbot_share_log'),
    path('chatbot/trusted-contacts/save/', views.trusted_contacts_save, name='trusted_contacts_save'),
    path('chatbot/trusted-contacts/load/', views.trusted_contacts_load, name='trusted_contacts_load'),
    path('panel/delete-alert/<int:alert_id>/', views.delete_emergency_alert, name='delete_emergency_alert'),
    path('panel/delete-chatbot-log/<int:log_id>/', views.delete_chatbot_log, name='delete_chatbot_log'),
    path('incident-timeline/', views.incident_timeline, name='incident_timeline'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('panel/run-cleanup/', views.run_cleanup_now, name='run_cleanup_now'),

]
