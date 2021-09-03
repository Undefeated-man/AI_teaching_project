from django import forms
import django.core.validators as validators


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': "bg-info", 'id': 'fileinp',
                                                                        'accept': '.xlsx', 'title': '', 'value': 'Step 1 Select Lecture Files'}),
                                 validators=[validators.FileExtensionValidator(['xlsx'])])
