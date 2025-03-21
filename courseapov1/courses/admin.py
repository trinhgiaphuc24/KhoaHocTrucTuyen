from django.contrib import admin
from courses.models import Course, Category, Lesson, Tag, User, Comment
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class LessonForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Lesson
        fields = '__all__'

class MyCourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'active', 'created_date', 'category']
    search_fields = ['subject']
    list_filter = ['id', 'created_date']
    list_editable = ['subject']
    readonly_fields = ['image_view']

    def image_view(self, course):
        return mark_safe(f"<img src='/static/{course.image.name}' width='200' />")

class MyLessonAdmin(admin.ModelAdmin):
    form = LessonForm


admin.site.register(Category)
admin.site.register(Course, MyCourseAdmin)
admin.site.register(Lesson, MyLessonAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(User)