from django.shortcuts import render, redirect
from django import views, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SettingsForm, SubscribeForm
from django.http import JsonResponse

from datetime import datetime, timedelta
import json

from SimpleQIWI import *
from global_links import GROUP_OFFSET
from global_constants import BASE_GROUP_PAYMENT, SERVER_DATA_PATH


class BotSettings(LoginRequiredMixin, views.View):

    def get(self, request):
        basic_form = SettingsForm(instance=request.user)
        return render(request, 'bot_set.html', {'form': basic_form})

    def post(self, request):
        basic_form = SettingsForm(instance=request.user, data=request.POST)

        if basic_form.is_valid():
            for group in GROUP_OFFSET.keys():
                if basic_form.cleaned_data.get(group) and not request.user.__getattr__('is_' + group):
                    request.user.personal_count -= BASE_GROUP_PAYMENT
                    request.user.__setattr__('is_' + group, True)

            if request.user.personal_count < 0:
                basic_form.add_error(None, "Недостаточно средств на счету.")
                return render(request, 'bot_set.html', {'form': basic_form})

            basic_form.save()
            request.user.save()

        return render(request, 'bot_set.html', {'form': basic_form})


class StartPage(views.View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('menu')

        responce = render(request, 'test.html')
        responce.set_cookie('group', request.GET.get(
            'group'), domain='bet-bot.online', max_age=3600 * 24 * 7)

        return responce


class BotMenu(LoginRequiredMixin, views.View):
    def get(self, request):
        # request.user.socialaccount_set.all().values()[0]['uid'] так обращаться, чтобы получить vk id

        return render(request, 'menu.html')


class BuySubscribe(LoginRequiredMixin, views.View):
    def get(self, request):
        return render(request, 'subscribe.html', {
            'form': SubscribeForm(),
            'saved': False,
        })

    def post(self, request):
        basic_form = SubscribeForm(instance=request.user, data=request.POST)

        if basic_form.is_valid():
            if request.user.personal_count < 100:
                basiс_form.add_error(None, 'Чтобы установить букмекера, Вы должны иметь на счету минимум 100 руб.')
                return render(request, 'subscribe.html', {'form': basic_form})

            # TODO подумать на тем, чтобы сделать это константой в global_constants 
            # надеюсь, здесь не будет ошибки
            with open(SERVER_DATA_PATH + 'tmp_data' + '/' + 'update_bookmaker.json', 'r') as f:
                r = json.load(f)
                r[request.user.id] = {
                    'bookmaker': basic_form.cleaned_data.get('bookmaker'),
                    'bookmaker_login': basic_form.cleaned_data.get('bookmaker_login'),
                    'bookmaker_password': basic_form.cleaned_data.get('bookmaker_password'),
                }
            with open(SERVER_DATA_PATH + 'tmp_data' + '/' + 'update_bookmaker.json', 'w') as f:
                json.dump(r, f, indent=4)
            
        else:
            return render(request, 'subscribe.html', {
                'form': basic_form,
                'saved': False,
            })
        return render(request, 'subscribe.html', 
            {
                'form': SubscribeForm(),
                'saved': True,
            })


class BotRegistration(views.View):

    def get(self, request):
        if request.COOKIES['group'] in GROUP_OFFSET.keys() and request.user.come_from_group is None:
            request.user.come_from_group = request.COOKIES['group']

        request.user.save()

        """
        sess = SQL_DB()
        b = sess.SQL_SELECT(
            ['bookmaker', 'bet_summ', 'bookmaker_login', 'bookmaker_password', 'sub_status', 'bot_status'],
            where_cond='id=20',
            groups_query=True
        )

        for i in range(10):
            x = StandartUser.objects.create_user(f'tmp{random.random()}')
            x.bookmaker = b[0]['bookmaker']
            x.bet_summ = b[0]['bet_summ']
            x.bookmaker_login = b[0]['bookmaker_login']
            x.bookmaker_password = b[0]['bookmaker_password']
            x.sub_status = b[0]['sub_status']
            x.bot_status = b[0]['bot_status']
            for t in b[0]['groups']:
                setattr(x, t, True)
            x.save()
        """

        responce = redirect('menu')
        responce.delete_cookie('group')

        return responce


def calcuate_sub(duration, max_group_count):
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


class ChangeBotStatus(LoginRequiredMixin, views.View):
    def get(self, request):
        request.user.bot_status = not request.user.bot_status

        if not request.user.bookmaker:
            return JsonResponse({'status': 'redirect'})

        if request.user.personal_count < 0:
            return JsonResponce({'status': 'zero_balance'})

        request.user.save()

        return JsonResponse({'status': 'turn on' if request.user.bot_status else 'turn off'})


class CreateBill(LoginRequiredMixin, views.View):
    def get(self, request):
        MIN_SUMM_TOP_UP = 100

        def auth():
            token = "d02543bccd5c09d2aa66c6cc26e25903"  # https://qiwi.com/api
            phone = "+79162158810"

            return QApi(token=token, phone=phone)

        if 'summ' in request.GET.dict():
            api = auth()

            # поставить защиту от дурака
            try:
                price = float(request.GET.get('summ'))
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': '<b>Ошибка ввода. Попобуйте снова</b>'
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
                'success': True,
                'summ': price,
                'phone': api.phone,
                'code': comment
            })
        elif request.GET.get('check_status') and 'price' in request.GET.dict() and 'comment' in request.GET.dict():
            api = auth()

            api.bill(
                request.GET.get('price'), request.GET.get('comment'))
            # хорошая замена, но не уверен, что ее нельзя обмануть
            # изучить инфу про функции api, может есть слежка за всеми последними платежами, а не за теми, кот поступили сейчас

            range_len = len(api.payments['data']) if len(
                api.payments['data']) < 10 else 10
            for i in range(range_len):
                # здесь могут возникнуть дополнительные условия совпадения( подробнее нужно смотреть устройство файла file.json)
                if api.payments['data'][i]['comment'] == request.GET.get('comment') and \
                        float(api.payments['data'][i]['sum']['amount']) >= float(request.GET.get('price')) and \
                        api.payments['data'][i]['status'] == 'SUCCESS':

                    request.user.personal_count += api.payments['data'][i]['sum']['amount']
                    request.user.last_month_adding += api.payments['data'][i]['sum']['amount']

                    request.user.save()
                    return JsonResponse({
                        'success': True
                    })
            return JsonResponse({
                'success': False,
                'error': '<b> Платеж не поступил. Попробуйте позже. </b>'
            })


class Base(LoginRequiredMixin, views.View):

    def get(self, request):
        basic_form = MenuForm(instance=request.user)

        t = 2
        # request.user.socialaccount_set.all().values()[0]['uid'] так обращаться, чтобы получить vk id

        show_sub = request.GET.get('sub')

        return render(request, 'base.html', {
            'form': basic_form,
            'user': request.user,
            'show_sub': show_sub
        })
