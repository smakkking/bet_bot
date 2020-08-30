from django.contrib import admin
from django.urls import path
from UserDataManagment import views
from django.conf.urls import include

from django.contrib.auth import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/settings/', views.BotSettings.as_view()),
    path('account/renew', views.UpdateData.as_view(), name='renew'),
    path('account/', include('django.contrib.auth.urls')),
    path('account/menu/', views.BotMenu.as_view()),
]
