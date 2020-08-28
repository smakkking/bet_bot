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

class MenuForm(ModelForm) :
    post_text = forms.CharField(widget=forms.Textarea(
        attrs={
            'rows' : 50,
            'cols' : 200,
        }
    ))
    class Meta :
        model = StandartUser
        fields = (
            'subscr_end_date',
            'post_text',
        )


    