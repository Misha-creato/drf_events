from django import forms

from utils.constants import EMAIL_TYPES

from notifications.models import EmailTemplate


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = [
            'email_type',
            'subject',
            'message',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        used_choices = EmailTemplate.objects.values_list('email_type', flat=True)
        if self.instance:
            current_choice = self.instance.email_type
            used_choices = [choice for choice in used_choices if choice != current_choice]
        self.fields['email_type'].choices = [
            choice for choice in EMAIL_TYPES if choice[0] not in used_choices
        ]
