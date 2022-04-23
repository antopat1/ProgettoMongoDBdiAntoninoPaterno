from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    btc_wallet = models.FloatField(default=0)
    dollar_wallet = models.FloatField(default=0)
    profit = models.FloatField(default=0)

# Create your models here.


class BuyOrder(models.Model):
    quantity = models.FloatField(default=0)
    price = models.FloatField(default=0)
    publication_time = models.DateTimeField(auto_now_add=True)
    associated_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class SellOrder(models.Model):
    quantity = models.FloatField(default=0)
    price = models.FloatField(default=0)
    publication_time = models.DateTimeField(auto_now_add=True)
    associated_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class EditDelete(models.Model):
    id_order = models.IntegerField()
    quantity = models.FloatField(default=0.00000001)
    price = models.FloatField(default=0.01)
    choice_change = models.CharField(max_length=8, default="MODIFICA")
