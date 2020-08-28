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
        # задать константный путь к файлу json
        file = open(r'C:\GitRep\bet_bot\user_data\group_post_data.json', 'r')
        data = json.load(file)
        new_data = {}
        user_data = SettingsForm(instance=request.user).__dict__['initial']
        for key in data.keys() :
            if key in user_data.keys() and user_data[key] :
                new_data[key] = data[key]
        # здесь должно быть отсеивание в зависимости от выбора пользователя
        basic_form = MenuForm(data={
            'post_text' : new_data,
            'end_date' : request.user.subscr_end_date,
        })
        file.close()
        return render(request, 'menu.html', {'form' : basic_form})
