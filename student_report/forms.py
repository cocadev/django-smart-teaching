from django import forms


class label_class(forms.Form):
    label = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Add Label'}))