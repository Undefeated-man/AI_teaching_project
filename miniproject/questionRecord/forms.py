from django import forms
import django.core.validators as validators


class FileFieldForm(forms.Form):
    file_field = forms.FileField(label='Step 1 Select Lecture Files', label_suffix='',
                                 widget=forms.ClearableFileInput( attrs={'multiple': True,'accept': '.xlsx', 'title': ''
                                     , 'style': "display:none", 'id': 'fileinp', 'onchange': 'FileDisplay()'}),
                                 validators=[validators.FileExtensionValidator(['xlsx'])])
