from django.contrib import admin
from django.urls import path
from bet_web import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('settings/', views.BotSettings.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
    path('menu/', views.BotMenu.as_view()),
]
