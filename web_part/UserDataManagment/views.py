from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DataForm
from .models import StandartUser

class BotSettings(LoginRequiredMixin, views.View) :
    def get(self, request) :
        basic_form = DataForm(instance=request.user)
        return render(request, 'bot_set.html', {'form' : basic_form})
    def post(self, request) :
        basic_form = DataForm(instance=request.user, data=request.POST)
        if basic_form.is_valid() :
            basic_form.save()
        return render(request, 'bot_set.html', {'form' : basic_form})

class BotMenu(LoginRequiredMixin, views.View) :
    def get(self, request) :

        return render(request, 'menu.html')
