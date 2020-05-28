from django import forms
from django.forms import ModelForm

from .models import ConfirmationCode


class ConfirmationForm(ModelForm):
    code = forms.CharField(required=False)

    class Meta:
        model = ConfirmationCode
        fields = '__all__'
