from django.contrib import admin
from django.urls import path
from UserDataManagment import views
from django.conf.urls import include

urlpatterns = [
    path('admin12wpWggyIoXk/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    path('', views.StartPage.as_view(), name='start_page'),

    path('menu/', views.BotMenu.as_view(), name='menu'),
    path('subscribe/', views.BuySubscribe.as_view(), name='subscribe'),
    path('settings/', views.BotSettings.as_view(), name='settings'),
    path('base/', views.Base.as_view()),

    path('manage/change_status',
         views.ChangeBotStatus.as_view(), name='change_status'),
    path('manage/add_to_account', views.CreateBill.as_view(), name='add'),
    path('manage/set_group', views.BotRegistration.as_view(), name='set_group')

]
