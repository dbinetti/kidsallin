
# Django
from django.contrib import admin

# Local
from .models import Student


class StudentInline(admin.TabularInline):
    model = Student
    fields = [
        'name',
        'parent',
        'school',
        'grade',
    ]
    readonly_fields = [
    ]
    ordering = [
        'grade',
        'name',
    ]
    show_change_link = True
    extra = 0
    classes = [
        # 'collapse',
    ]
    autocomplete_fields = [
        'school',
        'parent',
    ]
