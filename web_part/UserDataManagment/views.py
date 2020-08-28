from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm
from .models import StandartUser

import json

class BotSettings(LoginRequiredMixin, views.View) :
    def get(self, request) :
        basic_form = SettingsForm(instance=request.user)
        return render(request, 'bot_set.html', {'form' : basic_form})
    def post(self, request) :
        basic_form = SettingsForm(instance=request.user, data=request.POST)
        if basic_form.is_valid() :
            basic_form.save()
        return render(request, 'bot_set.html', {'form' : basic_form})

class BotMenu(LoginRequiredMixin, views.View) :
    def get(self, request) :
        file = open(r'C:\GitRep\bet_bot\user_data\group_post_data.json', 'r')
        basic_form = MenuForm(instance=request.user)
        file.close()
        return render(request, 'menu.html', {'form' : basic_form})
