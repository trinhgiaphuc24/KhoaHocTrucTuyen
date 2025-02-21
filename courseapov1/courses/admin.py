from django.contrib import admin
from courses.models import Course, Category

admin.site.register(Category)
admin.site.register(Course)
