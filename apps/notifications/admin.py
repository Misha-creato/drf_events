from django.contrib import admin

from solo.admin import SingletonModelAdmin

from notifications.forms import EmailTemplateForm
from notifications.models import (
    EmailTemplate,
    EmailSettings,
)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm
    list_display = [
        'email_type',
    ]


@admin.register(EmailSettings)
class EmailConfigurationAdmin(SingletonModelAdmin):
    pass
