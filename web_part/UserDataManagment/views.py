from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm, RegistrationForm, SubscribeForm
from .models import StandartUser

import json, sys
from datetime import datetime, timedelta


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
        basic_form = MenuForm(instance=request.user)
        return render(request, 'menu.html', {'form' : basic_form})

    def post(self, request) :
        request.user.bot_status = not request.user.bot_status
        request.user.save()

        basic_form = MenuForm(instance=request.user)
        return render(request, 'menu.html', {'form' : basic_form, 'bot_status' : request.user.bot_status})


class BuySubscribe(LoginRequiredMixin, views.View) :
    def get(self, request) :
        return render(request, 'subscribe.html', {'form' : SubscribeForm(instance=request.user)})
    def post(self, request) :
        basic_form = SubscribeForm(instance=request.user, data=request.POST)
        if basic_form.is_valid() :
            basic_form.save()
            # получаем время окончания подписки
            now = datetime.today()
            request.user.sub_end_date = now + timedelta(days=int(request.POST['week']) * 7)
            request.user.sub_status = True
            request.user.save()
        else :
            return self.get(request)
        return redirect('menu')


class BotRegistration(views.View) :
    def get(self, request) :
        user_form = RegistrationForm()
        return render(request, 'register.html', {'user_form': user_form})

    def post(self, request) :
        user_form = RegistrationForm(data=request.POST)
        if user_form.is_valid() :
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form['password'])
            new_user.save()
            # переделать на подтверждение по почте(сейчас просто переикдывает на страницу логина)
            return redirect('login')

