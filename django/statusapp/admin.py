from django.contrib import admin
from .models import StatusMessage

class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_at']
    search_fields = ['message']

admin.site.register(StatusMessage, StatusMessageAdmin)
