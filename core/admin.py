from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Attendance, AuditEvent, ClassSession, Enrolment, Offering, User


class PortalAdminSite(admin.AdminSite):
    site_header = 'UniSphere administration'
    site_title = 'UniSphere'
    index_title = 'Manage academic records'

    def has_permission(self, request):
        return super().has_permission(request) and request.user.role == 'admin'


portal_admin_site = PortalAdminSite(name='admin')


@admin.register(User, site=portal_admin_site)
class PortalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('UniSphere', {'fields': ('role', 'student_number')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('UniSphere', {'fields': ('role', 'first_name', 'last_name', 'email')}),)
    list_display = ['username', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']


@admin.register(Offering, site=portal_admin_site)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'semester', 'credits']
    filter_horizontal = ['lecturers']


@admin.register(Enrolment, site=portal_admin_site)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'offering']
    list_filter = ['offering']


@admin.register(ClassSession, site=portal_admin_site)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ['offering', 'topic', 'starts_at', 'venue', 'cancelled']
    list_filter = ['offering']


@admin.register(Attendance, AuditEvent, site=portal_admin_site)
class ReadOnlyRecordAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
