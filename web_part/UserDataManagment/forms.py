from django import forms
from .models import StandartUser

class DataForm(forms.Form) :
    bookmaker = forms.CharField(max_length=128)

    bookmaker_login = forms.CharField(max_length=128)
    bookmaker_password = forms.CharField(max_length=128)

    AcademiaStavok = forms.BooleanField()
    CSgoNorch = forms.BooleanField()


    