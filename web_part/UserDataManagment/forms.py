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

class MenuForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'sub_end_date',
            #'bot_status',
        )

class SubscribeForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'max_group_count',
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
            
        )
        

class RegistrationForm(ModelForm) :
    #no_bkm = forms.BooleanField(
    #    label='Регистрация без букмекера'
    #)
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


    