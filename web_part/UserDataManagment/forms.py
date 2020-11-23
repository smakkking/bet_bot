from django.forms import ModelForm
from .models import StandartUser
from django import forms
from moduls.bet_manage import GROUP_OFFSET

class SettingsForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'bet_summ',
        )
        fields += tuple(GROUP_OFFSET.keys())

class MenuForm(forms.Form) :
    end_date = forms.DateField(
        label='Дата окончания действия подписки'
    )

class RegistrationForm(ModelForm) :
    no_bookmaker = forms.BooleanField(
        label='no_bookmaker'
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput
    )
    class Meta :
        model = StandartUser
        fields = (
            'username',
            'email',
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password'
        )


    