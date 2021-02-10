from django.contrib import admin
from django.urls import path
from UserDataManagment import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.StartPage.as_view(), name='start_page'),
    path('account/registration/', views.BotRegistration.as_view(), name='registration'),
    path('account/settings/', views.BotSettings.as_view(), name='settings'),
    path('account/', include('django.contrib.auth.urls')),
    path('account/menu/', views.BotMenu.as_view(), name='menu'),
    path('account/subscribe/', views.BuySubscribe.as_view(), name='subscribe'),
    path('account/change_status', views.ChangeBotStatus.as_view(), name='change_status'),
    path('account/add_to_account', views.CreateBill.as_view(), name='add')

]
