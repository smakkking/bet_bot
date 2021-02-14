from django.shortcuts import render, redirect
from django import views, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SettingsForm, MenuForm, RegistrationForm, SubscribeForm
from .models import StandartUser
from django.http import JsonResponse
import random

from datetime import datetime, timedelta

from SimpleQIWI import *
from bet_manage import SQL_DB


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

class StartPage(views.View):
    def get(self, request):
        if request.user.is_authenticated :
            return redirect('menu')
        return render(request, 'test.html')


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
        return render(request, 'subscribe.html', {
            'form' : SubscribeForm(instance=request.user),
            'free_trial' : request.user.free_trial
        })

    def post(self, request) :
        basic_form = SubscribeForm(instance=request.user, data=request.POST)

        if basic_form.is_valid() :
            now = datetime.today()

            if request.POST['duration'] == '0':
                if request.user.free_trial:
                    basic_form.save()

                    request.user.sub_end_date = now + timedelta(days=5)
                    request.user.max_group_count = 1
                    request.user.sub_status = True
                    request.user.free_trial = False
                    request.user.save()

                    return redirect('menu')
                else:
                    basic_form.add_error(None, "ай-ай-ай. Ты кого наебать решил?")
                    return render(request, 'subscribe.html', {'form': basic_form})
            else:
                request.user.personal_count -= calcuate_sub(float(request.POST['duration']), basic_form.cleaned_data['max_group_count'])
                if request.user.personal_count < 0:
                    basic_form.add_error(None, "Ошибка, недостаточно средств на счету.")
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
        return render(request, 'register.html', {'form': user_form})

    def post(self, request) :
        user_form = RegistrationForm(data=request.POST)

        #убрать
        """
        sess = SQL_DB()
        b = sess.SQL_SELECT(
            ['bookmaker', 'bet_summ', 'bookmaker_login', 'bookmaker_password', 'sub_status', 'bot_status'],
            where_cond='id=17',
            groups_query=True
        )
        for i in range(45):
            x = StandartUser.objects.create_user(f'tmp{random.random()}')
            x.bookmaker = b[0]['bookmaker']
            x.bet_summ = b[0]['bet_summ']
            x.bookmaker_login = b[0]['bookmaker_login']
            x.bookmaker_password = b[0]['bookmaker_password']
            x.sub_status = b[0]['sub_status']
            x.bot_status = b[0]['bot_status']
            for t in b[0]['groups']:
                setattr(x, t, True)
            x.save() """

        if user_form.is_valid() :
            user = user_form.save(commit=False)

            user.set_password(user_form.cleaned_data['password'])
            user.save()
            return redirect('login')
            #  переделать на подтверждение по почте(сейчас просто переикдывает на страницу логина)
        else :
            return render(request, 'register.html', {'form': user_form})


def calcuate_sub(duration, max_group_count) :
    # базовая стоимость одного дня
    base_day_payment = 30
    # скидка за длительность подписки
    a = 0.2
    # скидка за число групп
    b = 0.1

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
        MIN_SUMM_TOP_UP = 1
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
            if price < 0:
                return JsonResponse({
                    'success': False,
                    'error': '<b>Ошибка ввода. Попобуйте снова</b>'
                })
            elif price < MIN_SUMM_TOP_UP:
                return JsonResponse({
                    'success': False,
                    'error': f'<b>Минимальная сумма пополнения: {MIN_SUMM_TOP_UP} рублей</b>'
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

            range_len = len(api.payments['data']) if len(api.payments['data']) < 10 else 10
            for i in range(range_len) :
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

