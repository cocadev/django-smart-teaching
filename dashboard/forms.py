from django import forms
from .models import csvfile


class file_class(forms.ModelForm):
    req_file = forms.FileField(widget=forms.FileInput(attrs={'id': 'file-input', 'class': 'image-upload'}))

    class Meta:
        model = csvfile
        fields = ('req_file',)

