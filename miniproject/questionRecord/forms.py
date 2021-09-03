from django import forms
import django.core.validators as validators


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': "bg-info", 'id': "fileupload",
                                                                        'accept': '.xlsx', 'title': '', 'style': "display:none;"}),
                                 validators=[validators.FileExtensionValidator(['xlsx'])])
