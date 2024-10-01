from django.contrib import admin
from .models import ContactSetting, ContactSubject, ContactUs


@admin.register(ContactSetting)
class ContactSettingAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactSubject)
class ContactSubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "number", "is_checked", "date_created")
    list_filter = ("subject",)
    search_fields = ("title",)

