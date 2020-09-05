from django.contrib import admin
from django.urls import path
from UserDataManagment import views
from django.conf.urls import include
from django.views.generic import TemplateView

from django.contrib.auth import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="test.html")),
    path('account/settings/', views.BotSettings.as_view()),
    path('account/renew', views.UpdateData.as_view(), name='renew'),
    path('account/bet', views.BetData.as_view(), name='bet'),
    path('account/', include('django.contrib.auth.urls')),
    path('account/menu/', views.BotMenu.as_view()),
]
