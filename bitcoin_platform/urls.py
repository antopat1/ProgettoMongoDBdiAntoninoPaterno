"""bitcoin_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from access_register.views import homepage, registrazion, searchDeleteOrModify
from exchange_utility.views import activBuyOrders, activSellOrders, exportJsonByCollectionMdb, profitsOrLoss
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="homepage"),
    path('registrazione/', registrazion, name="registrazione"),
    path('searchDeleteOrModify/<str:sell_or_buy>/<str:singleOrAll>/',
         searchDeleteOrModify, name="searchDeleteOrModify"),
    path('JsonActivBuyOrders/<str:singleOrAll>/',
         activBuyOrders, name="activBuyOrders"),
    path('JsonActivSellOrders/<str:singleOrAll>/',
         activSellOrders, name="activSellOrders"),
    path('exportJsonByCollectionMdb/<str:choose_export>/',
         exportJsonByCollectionMdb, name="exportJsonByCollectionMdb"),
    path('profitsOrLoss/', profitsOrLoss, name="profitsOrLoss"),
    path('account/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('', include('exchange_utility.urls')),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
