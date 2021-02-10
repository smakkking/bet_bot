from django.forms import ModelForm, TextInput
from .models import StandartUser
from django import forms
from django.forms.widgets import Widget

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
            'personal_count',
            'username',
        )
        widgets = {
            'personal_count' : TextInput(attrs={'readonly':'readonly'}),
            'sub_end_date' : TextInput(attrs={'readonly':'readonly'})
        }


class RangeWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        x = f"""
            <input  name="{name}" 
                    value="{value}" 
                    type="range" 
                    id="{attrs['id']}"
                    step="1"
                    min="1"
                    max="{len(GROUP_OFFSET.keys())}"
                    list="rangeList"
                    onchange="document.getElementById('rangeValue').innerHTML = this.value;"
            >
            <datalist id="rangeList">        
        """
        for i in range(1, len(GROUP_OFFSET.keys()) + 1):
            x += f'<option value="{i}" label="{i}">'
        x += '</datalist><span id="rangeValue">1</span>'
        return x


class SubscribeForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'max_group_count',
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
        )
        widgets = {
            'max_group_count' : RangeWidget()
        }

        

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
        )
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Ошибка, пароли не совпадают. Повторите ввод.")
        return cd['password2']


