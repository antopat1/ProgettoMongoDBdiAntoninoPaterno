from django.urls import path
from .views import publishBidOrder,publishAskOrder

urlpatterns = [
    path('publishBidOrder/', publishBidOrder , name='publishBidOrder'),
    path('publishAskOrder/', publishAskOrder , name='publishAskOrder'),
]