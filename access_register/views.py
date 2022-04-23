from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse
from .forms import FormRegistrazionUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from exchange_utility.models import Customer, BuyOrder, SellOrder
from exchange_utility.forms import ChoiceForm
import random
import requests
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


class Bot_cmkCap_interface:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': 1,
            'limit': 1,
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '0a2fb2a6-05a5-4731-8f4f-19090466df18'
        }

    def process_current_data(self):
        r = requests.get(url=self.url, headers=self.headers,
                         params=self.params).json()
        return r['data']


def current_btc_value():
    bot = Bot_cmkCap_interface()
    current_price = bot.process_current_data()
    return current_price[0]['quote']['USD']['price']


# Create your views here.
def homepage(request):
    buy_bookOrder = BuyOrder.objects.filter().order_by('-publication_time')
    sell_bookOrder = SellOrder.objects.filter().order_by('-publication_time')
    if request.user.is_authenticated and not request.user.is_superuser:
        current_customer = Customer.objects.get(user=request.user)
        btc_balance = round(current_customer.btc_wallet, 2)
        cust_dollar = round(current_customer.dollar_wallet, 2)
        actual_dollar_BTC = round(
            (current_customer.btc_wallet * current_btc_value()), 2)  # 1
        context = {'current_customer': current_customer, 'buy_bookOrder': buy_bookOrder,
                   'sell_bookOrder': sell_bookOrder, 'actual_dollar_BTC': round(actual_dollar_BTC, 2), 'btc_balance': round(btc_balance, 2), 'cust_dollar': cust_dollar, }
    else:
        current_customer = None
        context = {'current_customer': current_customer,
                   'buy_bookOrder': buy_bookOrder, 'sell_bookOrder': sell_bookOrder}
    return render(request, "access_register/homepage.html", context)


def registrazion(request):
    if request.method == "POST":
        form = FormRegistrazionUser(request.POST)
        try:
            if form.is_valid():
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                new_user = User.objects.create_user(
                    username=username, password=password, email=email)
                new_customer = Customer(
                    user=new_user,
                    btc_wallet=random.randrange(1, 11),
                )
                new_customer.dollar_wallet = new_customer.btc_wallet * \
                    round(current_btc_value(), 2)  # 2
                new_customer.save()
                new_user = authenticate(username=username, password=password)
                login(request, new_user)

                messages.error(
                    request, f'Benvenuto/a! {new_customer.user.username}, la piattaforma attribuisce i seguenti bitcoin al tuo wallet : {new_customer.btc_wallet}')
                return redirect('/')
        except:
            messages.error(
                request, 'Attenzione non hai inserito tutti i dati necessari per la creazione nuova utenza!')
            return redirect('/registrazione/')
    else:
        form = FormRegistrazionUser()
    context = {"form": form}
    return render(request, "registration/registrazione.html", context)


@login_required()
def searchDeleteOrModify(request, sell_or_buy, singleOrAll):
    costoumer_buy_Orders = None
    costoumer_sell_Orders = None
    try:
        current_customer = Customer.objects.get(user=request.user)
    except ObjectDoesNotExist:  # per gestire l'eccezione dell'Admin iniziale creato da Terminale
        costoumer_buy_Orders = BuyOrder.objects.filter().order_by('-publication_time')
        costoumer_sell_Orders = SellOrder.objects.filter().order_by('-publication_time')
        current_customer = None

    if singleOrAll == "single":
        costoumer_buy_Orders = BuyOrder.objects.filter(
            associated_customer=current_customer).order_by('-publication_time')
        costoumer_sell_Orders = SellOrder.objects.filter(
            associated_customer=current_customer).order_by('-publication_time')

    elif singleOrAll == "all":
        costoumer_buy_Orders = BuyOrder.objects.filter().order_by('-publication_time')
        costoumer_sell_Orders = SellOrder.objects.filter().order_by('-publication_time')

    if current_customer == None:
        actual_dollar_BTC = 0

    else:
        actual_dollar_BTC = round(
            (current_customer.btc_wallet * current_btc_value()), 2)  # 3

    if request.method == "POST":
        form_id = ChoiceForm(request.POST)

        if form_id.is_valid():
            choice = form_id.save(commit=False)
            orderSearch = int(choice.id_order)
            changeQuantity = float(choice.quantity)
            changePrice = float(choice.price)
            decideChange = str(choice.choice_change)
            goal = False

            if sell_or_buy == "BUY":

                if changeQuantity <= 0.0 or changePrice <= 0.0:
                    messages.error(
                        request, 'Non puoi inserire quantità o prezzi negativi o nulli')
                    return redirect('/')

                if decideChange == 'MODIFICA':
                    if request.user.is_superuser:
                        messages.error(
                            request, 'Modifica non consentita per leggittimità piattaforma e correttezza verso utenti')
                        return redirect('/')
                    for order in costoumer_buy_Orders:
                        if order.id == orderSearch:
                            old_price = order.price
                            order.quantity = changeQuantity
                            order.price = changePrice
                            # riaccredito il saldo congelato in fase di piazzamento ordine
                            current_customer.dollar_wallet += old_price
                            if current_customer.dollar_wallet < changePrice:
                                messages.error(
                                    request, 'Non hai sufficienti fondi per piazzare questo ordine ')
                                return redirect('/')
                            else:
                                # congelo il budget per il nuovo ordine appena modificato
                                current_customer.dollar_wallet -= changePrice
                                order.save()
                                current_customer.save()
                                goal = True
                                messages.error(
                                    request, 'Modifica eseguita con successo! ')
                                return redirect('/')
                    if goal == False:
                        messages.error(
                            request, 'Probabilmente hai inserito un ID ordine non della tua lista ')
                        return redirect('/')

                elif decideChange == 'CANCELLA':

                    for order in costoumer_buy_Orders:
                        if order.id == orderSearch:
                            goal = True
                            if not request.user.is_superuser:
                                # riaccredito il saldo congelato in fase di piazzamento ordine
                                current_customer.dollar_wallet += order.price
                                order.delete()
                                current_customer.save()

                            else:
                                order.associated_customer.dollar_wallet += order.price
                                order.delete()
                                order.associated_customer.save()

                            messages.error(
                                request, 'Ordine cancellato con successo! ')
                            return redirect('/')
                    if goal == False:
                        messages.error(
                            request, 'Probabilmente hai inserito un ID ordine non della tua lista ')
                        return redirect('/')

            elif sell_or_buy == "SELL":

                if changeQuantity <= 0.0 or changePrice <= 0.0:
                    messages.error(
                        request, 'Non puoi inserire quantità o prezzi negativi o nulli')
                    return redirect('/')

                if decideChange == 'MODIFICA':
                    if request.user.is_superuser:
                        messages.error(
                            request, 'Modifica non consentita per leggittimità piattaforma e correttezza verso utenti')
                        return redirect('/')
                    for order in costoumer_sell_Orders:
                        if order.id == orderSearch:
                            old_quantity = order.quantity
                            order.quantity = changeQuantity
                            order.price = changePrice
                            # riaccredito il saldo congelato in fase di piazzamento ordine
                            current_customer.btc_wallet += old_quantity
                            if current_customer.btc_wallet < changeQuantity:
                                messages.error(
                                    request, 'Il tuo wallet non dispone della quanità di BTC indicata! ')
                                return redirect('/')
                            else:
                                # congelo il budget per il nuovo ordine appena modificato
                                current_customer.btc_wallet -= changeQuantity
                                order.save()
                                current_customer.save()
                                goal = True
                                messages.error(
                                    request, 'Modifica eseguita con successo! ')
                                return redirect('/')
                    if goal == False:
                        messages.error(
                            request, 'Probabilmente hai inserito un ID ordine non della tua lista ')
                        return redirect('/')

                elif decideChange == 'CANCELLA':
                    for order in costoumer_sell_Orders:
                        if order.id == orderSearch:
                            goal = True
                            if not request.user.is_superuser:
                                # riaccredito il saldo congelato in fase di piazzamento ordine
                                current_customer.btc_wallet += order.quantity
                                current_customer.profit = current_customer.profit
                                order.delete()
                                current_customer.save()
                            else:
                                order.associated_customer.btc_wallet += order.quantity
                                order.associated_customer.profit = order.associated_customer.profit
                                order.delete()
                                order.associated_customer.save()
                            messages.error(
                                request, 'Ordine cancellato con successo! ')
                            return redirect('/')
                    if goal == False:
                        messages.error(
                            request, 'Probabilmente hai inserito un ID ordine non della tua lista ')
                        return redirect('/')

        else:
            messages.error(
                request, 'ALERT! Ripeti operazione: Inserire MODIFICA per modificare i parametri di un ordine oppure inserire CANCELLA per eliminarlo definivamente dall OrderBook')
            return redirect('/')

    else:
        form_id = ChoiceForm()
        context = {"form_id": form_id, 'costoumer_buy_Orders': costoumer_buy_Orders,
                   'costoumer_sell_Orders': costoumer_sell_Orders, 'actual_dollar_BTC': actual_dollar_BTC}
        if sell_or_buy == "BUY":
            return render(request, "explore_orders/customer_orders_buy.html", context)
        elif sell_or_buy == "SELL":
            return render(request, "explore_orders/customer_orders_sell.html", context)
