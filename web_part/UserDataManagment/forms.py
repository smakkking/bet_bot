from django.forms import ModelForm, CheckboxSelectMultiple
from .models import StandartUser
from django import forms

class SettingsForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
            'max_bet_count',
            'balance_coefficient',
            'AcademiaStavok',
            'CSgoNorch',
            'CSgoVictory',
        )

class MenuForm(forms.Form) :
    end_date = forms.DateField(
        label='Дата окончания действия подписки'
    )


    