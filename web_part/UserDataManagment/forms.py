from django.forms import ModelForm
from .models import StandartUser
from django import forms

from global_constants import GROUP_OFFSET


class SettingsForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'bet_summ',
        )
        fields += tuple(GROUP_OFFSET.keys())
        
    def validate_groups(self, count) :
        cd = self.clean()
        k = 0
        for x in tuple(GROUP_OFFSET.keys()) :
            if cd.get(x) :
                k += 1
        if k > count :
            return False
        return True


class MenuForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'sub_end_date',
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
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Password again', 
        widget=forms.PasswordInput
    )
    class Meta :
        model = StandartUser
        fields = (
            'username',
            'email',
        )
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


    