from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django import views, forms
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SettingsForm, MenuForm, RegistrationForm, SubscribeForm
from .models import StandartUser
from moduls.bet_manage import BOOKMAKER_OFFSET

import json, sys, time
from datetime import datetime, timedelta


class BotSettings(LoginRequiredMixin, views.View) :

    def get(self, request) :
        basic_form = SettingsForm(instance=request.user)
        return render(request, 'bot_set.html', {'form' : basic_form})

    def post(self, request) :
        basic_form = SettingsForm(instance=request.user, data=request.POST)
        
        if basic_form.is_valid() and basic_form.validate_groups(request.user.max_group_count):
            basic_form.save()
        else :
            basic_form.add_error(None, forms.ValidationError(f'Вы не можете выбрать больше {request.user.max_group_count} групп(ы)'))

        return render(request, 'bot_set.html', {'form' : basic_form})


class BotMenu(LoginRequiredMixin, views.View) :
    def get(self, request) :
        basic_form = MenuForm(instance=request.user)
        return render(request, 'menu.html', {
            'form' : basic_form, 
            'bot_status' : request.user.bot_status, 
            'sub_status' : request.user.sub_status,
        })

    def post(self, request) :
        request.user.bot_status = not request.user.bot_status
        request.user.save()

        basic_form = MenuForm(instance=request.user)
        return render(request, 'menu.html', {
            'form' : basic_form, 
            'bot_status' : request.user.bot_status, 
            'sub_status' : request.user.sub_status,
        })


class BuySubscribe(LoginRequiredMixin, views.View) :

    def get(self, request) :
        return render(request, 'subscribe.html', {'form' : SubscribeForm(instance=request.user)})

    def post(self, request) :
        basic_form = SubscribeForm(instance=request.user, data=request.POST)
        if basic_form.is_valid() :
            basic_form.save()

            now = datetime.today()
            request.user.sub_end_date = now + timedelta(days=int(request.POST['week']) * 7 + 1)
            request.user.sub_status = True

            if request.user.chrome_dir_path is None :
                request.user.chrome_dir_path = str(time.time()).replace('.', '')
            request.user.save()

            if not BOOKMAKER_OFFSET[request.user.bookmaker].HAS_API :                
                BOOKMAKER_OFFSET[request.user.bookmaker].login(user=request.user)
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
            user = user_form.save(commit=False)

            user.set_password(user_form.cleaned_data['password'])
            user.save()
            return redirect('login')
            #  переделать на подтверждение по почте(сейчас просто переикдывает на страницу логина)
        else :
            return self.get(request)

    