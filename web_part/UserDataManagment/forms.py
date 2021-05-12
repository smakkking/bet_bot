from django.forms import ModelForm, TextInput
from .models import StandartUser
from django import forms
from django.forms.widgets import Widget, RadioSelect

from global_links import GROUP_OFFSET


class SettingsForm(ModelForm):
    class Meta:
        model = StandartUser
        fields = (
            'bet_mode',
            'bet_summ',
        )
        fields += tuple(GROUP_OFFSET.keys())
        widgets = {
            'bet_mode': RadioSelect(),
        }

    def validate_groups(self, count):
        cd = self.clean()
        k = 0
        for x in tuple(GROUP_OFFSET.keys()):
            if cd.get(x):
                k += 1
        if k > count:
            return False
        return True


class SubscribeForm(ModelForm):
    class Meta:
        model = StandartUser
        fields = (
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
        )
        widgets = {
        }
