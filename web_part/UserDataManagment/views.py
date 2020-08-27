from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DataForm
from .models import StandartUser

class BotSettings(LoginRequiredMixin, views.View) :
    def get(self, request) :
        old_data = {
            'bookmaker' : request.user.bookmaker, 
             'bookmaker_login' : request.user.bookmaker_login, 
             'bookmaker_password' : request.user.bookmaker_password, 
             'AcademiaStavok' : request.user.AcademiaStavok,
             'CSgoNorch' : request.user.CSgoNorch,
        }
        basic_form = DataForm(old_data)
        return render(request, 'bot_set.html', {'form' : basic_form})
    def post(self, request) :
        print('POST data')
        data = dict(request.POST)
        del data['csrfmiddlewaretoken']
        for key in data :
            exec('request.user.' + str(key) +'= data[key][0]')
        return self.get(request)

class BotMenu(LoginRequiredMixin, views.View) :
    def get(self, request) :

        return render(request, 'menu.html')
