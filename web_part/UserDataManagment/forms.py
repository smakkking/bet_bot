from django.forms import ModelForm
from .models import StandartUser

class DataForm(ModelForm) :
    class Meta :
        model = StandartUser
        fields = (
            'bookmaker',
            'bookmaker_login',
            'bookmaker_password',
            'AcademiaStavok',
            'CSgoNorch',
        )


    