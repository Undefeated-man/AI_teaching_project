from django import forms


file_field = forms.FileField(label='选择多个文件',help_text='提示：注意*****',
                                 widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': "bg-info"}))
