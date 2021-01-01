from django.shortcuts import render, redirect
from django import views, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SettingsForm, MenuForm, RegistrationForm, SubscribeForm
from django.http import JsonResponse

from datetime import datetime, timedelta

from SimpleQIWI import *
from time import sleep
import json


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
        pass

class BuySubscribe(LoginRequiredMixin, views.View) :

    def get(self, request) :
        return render(request, 'subscribe.html', {'form' : SubscribeForm(instance=request.user)})

    def post(self, request) :
        basic_form = SubscribeForm(instance=request.user, data=request.POST)

        if basic_form.is_valid() :

            request.user.personal_count -= calcuate_sub(float(request.POST['duration']), basic_form.cleaned_data['max_group_count'])
            if request.user.personal_count < 0:
                basic_form.add_error('max_group_count', "Ошибка, недостаточно средств на счету.")
                return render(request, 'subscribe.html', {'form': basic_form})

            basic_form.save()

            now = datetime.today()
            request.user.sub_end_date = now + timedelta(days=float(request.POST['duration']) * 31)
            request.user.sub_status = True

            request.user.save()
        else :
            return render(request, 'subscribe.html', {'form' : basic_form})
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


def calcuate_sub(duration, max_group_count) :
    base_day_payment = 30
    a = 0.2
    b = 0.14

    sale_mn = 0
    if duration == 1:
        sale_mn = 1
    elif duration == 3:
        sale_mn = 2
    elif duration == 6:
        sale_mn = 3

    count_sale = (1 - b) ** (max_group_count - 1)
    duration_sale = (1 - a) ** sale_mn

    S = base_day_payment * duration * 31 * duration_sale * count_sale
    return S * max_group_count


class ChangeBotStatus(LoginRequiredMixin, views.View) :
    def get(self, request) :
        request.user.bot_status = not request.user.bot_status
        request.user.save()

        return JsonResponse({'status': request.user.bot_status})


class CreateBill(LoginRequiredMixin, views.View) :
    # не работает
    def get(self, request) :
        def auth():
            token = "d02543bccd5c09d2aa66c6cc26e25903"  # https://qiwi.com/api
            phone = "+79162158810"

            return QApi(token=token, phone=phone)

        if 'summ' in request.GET.dict() :
            api = auth()

            # поставить защиту от дурака
            try :
                price = float(request.GET.get('summ'))
            except ValueError:
                return JsonResponse({
                    'success' : False,
                    'error' : '<b>Ошибка ввода. Попобуйте снова</b>'
                })
            if price < 0 :
                return JsonResponse({
                    'success': False,
                    'error': '<b>Ошибка ввода. Попобуйте снова</b>'
                })

            comment = api.bill(price)

            return JsonResponse({
                'success' : True,
                'summ' : price,
                'phone' : api.phone,
                'code' : comment
            })
        elif request.GET.get('check_status') and 'price' in request.GET.dict() and 'comment' in request.GET.dict():
            api = auth()

            api.bill(
                request.GET.get('price'), request.GET.get('comment'))
            # хорошая замена, но не уверен, что ее нельзя обмануть
            # изучить инфу про функции api, может есть слежка за всеми последними платежами, а не за теми, кот поступили сейчас


            for i in range(6) :
                # здесь могут возникнуть дополнительные условия совпадения( подробнее нужно смотреть устройство файла file.json)
                if api.payments['data'][i]['comment'] == request.GET.get('comment') and \
                        float(api.payments['data'][i]['sum']['amount']) >= float(request.GET.get('price')) and \
                        api.payments['data'][i]['status'] == 'SUCCESS':
                    request.user.personal_count += api.payments['data'][i]['sum']['amount']
                    request.user.save()
                    return JsonResponse({
                        'success' : True
                    })
            return JsonResponse({
                'success' : False,
                'error' : '<b> Платеж не поступил. Попробуйте позже. </b>'
            })

