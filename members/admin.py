from django.contrib import admin

from .models import Member, Family


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "email", "birthday", "license", "phone", "is_organization_admin", "created", "modified"]
    list_filter = ["is_organization_admin"]
    ordering = ["user__last_name", "user__first_name"]
    date_hierarchy = "birthday"
    search_fields = ["user__last_name", "user__first_name", "user__email", "license", "phone"]
    raw_id_fields = ["user"]
    fieldsets = [
        ["GENERAL INFORMATION", {"fields": ["user", "birthday", "phone"]}],
        ["EMERGENCY CONTACTS", {"fields": ["emergency_phone_primary", "emergency_phone_secondary"]}],
        ["CLUB INFORMATION", {"fields": ["license", "is_organization_admin"]}],
        ["OTHER", {"fields": ["password_change_required", "notes"]}],
    ]


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ["id", "created", "modified"]
    filter_horizontal = ["members"]
    fieldsets = [
        ["GENERAL INFORMATION", {"fields": ["members"]}],
    ]
