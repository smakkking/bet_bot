from django.forms import ModelForm, CheckboxSelectMultiple
from .models import StandartUser
from django import forms
from moduls.bet_manage import GROUP_OFFSET

class SettingsForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
            'bet_summ',
        )
        fields += tuple(GROUP_OFFSET.keys())

class MenuForm(forms.Form) :
    end_date = forms.DateField(
        label='Дата окончания действия подписки'
    )


    