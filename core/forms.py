from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

from .models import Assignment, Feedback, Resource


class RoleLoginForm(AuthenticationForm):
    error_messages = {'invalid_login': 'The account details or selected portal are incorrect.', 'inactive': 'This account is unavailable.'}

    def __init__(self, *args, role, **kwargs):
        self.role = role
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(autocomplete='username', autofocus=True)
        self.fields['password'].widget.attrs.update(autocomplete='current-password')

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.role != self.role:
            raise forms.ValidationError(self.error_messages['invalid_login'], code='invalid_login')


def validate_document(file):
    if file.size > 5 * 1024 * 1024:
        raise forms.ValidationError('Choose a PDF or text file smaller than 5 MB.')
    suffix = Path(file.name).suffix.lower()
    if suffix not in {'.pdf', '.txt'}:
        raise forms.ValidationError('This milestone accepts PDF and plain text files only.')
    sample = file.read(2048)
    file.seek(0)
    if suffix == '.pdf' and not sample.startswith(b'%PDF-'):
        raise forms.ValidationError('This file does not appear to be a PDF.')
    if suffix == '.txt':
        try:
            sample.decode('utf-8')
        except UnicodeDecodeError:
            raise forms.ValidationError('Choose a UTF-8 plain text file.')
        if b'\x00' in sample:
            raise forms.ValidationError('Choose a plain text file rather than a binary file.')
    return file


class SubmissionForm(forms.Form):
    file = forms.FileField(label='Your assignment', validators=[validate_document], help_text='PDF or UTF-8 text, up to 5 MB. A completed upload creates a receipt.')


class AssignmentForm(forms.ModelForm):
    publish = forms.BooleanField(required=False, label='Publish to enrolled students now')

    class Meta:
        model = Assignment
        fields = ['offering', 'title', 'instructions', 'due_at', 'max_score', 'allow_late']
        widgets = {'due_at': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}), 'instructions': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offering'].queryset = user.teaching.all()
        self.fields['due_at'].help_text = 'Malaysia time (UTC+8).'

    def clean_due_at(self):
        value = self.cleaned_data['due_at']
        if value <= timezone.now():
            raise forms.ValidationError('Choose a future deadline.')
        return value


class FeedbackForm(forms.ModelForm):
    release = forms.BooleanField(required=False, label='Release this feedback to the student')

    class Meta:
        model = Feedback
        fields = ['mark', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'file']

    def clean_file(self):
        return validate_document(self.cleaned_data['file'])
