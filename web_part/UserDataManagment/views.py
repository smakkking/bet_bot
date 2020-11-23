from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm, RegistrationForm
from .models import StandartUser

import json
import sys

from manage import ALL_POSTS_JSON_PATH


class BotSettings(LoginRequiredMixin, views.View) :
    def get(self, request) :
        basic_form = SettingsForm(instance=request.user)
        return render(request, 'bot_set.html', {'form' : basic_form})
    def post(self, request) :
        # поменять настройки у usera
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

        return response

    def post(self, request) :
        request.user.bot_status = not request.user.bot_status

        request.user.save()
        basic_form = MenuForm(data={
            'end_date' : request.user.sub_end_date,
        })
        response = render(request, 'menu.html', {'form' : basic_form})

        return response


class BuySubscribe(LoginRequiredMixin, views.View) :
    def get(self, request) :
        return render(request, 'subscribe.html')


class BotRegistration(LoginRequiredMixin, views.View) :
    def get(self, request) :
        user_form = RegistrationForm()
        return render(request, 'register.html', {'user_form': user_form})

    def post(self, request) :
        user_form = RegistrationForm(data=request.POST)
        if user_form.is_valid() :
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.password)
            new_user.save()
            return render(request, 'register_done.html')