from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.universties_portal.models import Course
from apps.core.admin_site import admin_site


@admin.register(Course, site=admin_site)
class CourseAdmin(ModelAdmin):
    list_display = ("course_id", "name", "institute_name", "degreelevel_name", "discipline_name")
    search_fields = ("=course_id", "name", "institute_name", "course_slug", "institute_slug")
    list_filter = ("degreelevel_name", "discipline_name", "course_language", "currency")
