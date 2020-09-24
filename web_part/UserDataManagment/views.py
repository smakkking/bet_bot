from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm
from .models import StandartUser

import json
import sys

from moduls.all_scripts import checking_for_bets
from manage import ALL_POSTS_JSON_PATH


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
        basic_form = MenuForm(data={
            'end_date' : request.user.subscr_end_date,
        })
        response = render(request, 'menu.html', {'form' : basic_form})
        response.set_cookie('sub_status', request.user.subscribe_status)
        return response


class UpdateData(LoginRequiredMixin, views.View) :
    def get(self, request) :
        with open(ALL_POSTS_JSON_PATH, 'r') as f :
            data = json.load(f)
            new_data = {}
            user_data = SettingsForm(instance=request.user).__dict__['initial']
            for key in data.keys() :
                if key in user_data.keys() and user_data[key] :
                    new_data[key] = data[key]
            
        return JsonResponse(new_data, safe=False)


class BetData(LoginRequiredMixin, views.View) :
    def get(self, request) :
        def parse_json(data) :
            expected_keys = SettingsForm(instance=request.user).__dict__['initial'].keys()
            for key in data.keys() :
                if key in expected_keys and data[key][0] != 'old':
                    data[key] = json.loads(data[key][0])
                else :
                    data[key] = data[key][0] 
        bet_info = dict(request.GET)
        del bet_info['_']
        parse_json(bet_info)
        # здесь и должна вызываться функция ставки
        checking_for_bets(request.user, bet_info)
        return JsonResponse(bet_info, safe=False)


class BuySubscribe(LoginRequiredMixin, views.View) :
    def get(self, request) :
        print('ahah')
        return render(request, 'subscribe.html')
