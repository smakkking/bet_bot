from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import views
from django.middleware.csrf import get_token

from django.contrib.auth.mixins import LoginRequiredMixin

class BotSettings(LoginRequiredMixin, views.View) :
    def get(self, request) :
        return render(request, 'bot_set.html')
    def post(self, request) :
        print('POST data')
        print(dict(request.POST))
        return render(request, 'bot_set.html')

class BotMenu(LoginRequiredMixin, views.View) :
    def get(self, request) :
        return HttpResponse('Hello! i am main menu')

        

        