from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'phone', 'email', 'experience_years', 'created_at')
    list_filter = ('specialization', 'created_at')
    search_fields = ('name', 'email', 'specialization', 'phone')
    readonly_fields = ('created_at', 'updated_at')
