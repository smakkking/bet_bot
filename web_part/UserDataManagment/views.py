from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm
from .models import StandartUser

import json
import sys

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
            'end_date' : request.user.sub_end_date,
        })
        response = render(request, 'menu.html', {'form' : basic_form})
        #response.set_cookie('sub_status', request.user.sub_status)
        return response


class BuySubscribe(LoginRequiredMixin, views.View) :
    def get(self, request) :
        return render(request, 'subscribe.html')
