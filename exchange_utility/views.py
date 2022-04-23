from django.shortcuts import render, redirect
from .models import Customer, BuyOrder, SellOrder
from .forms import FormToPublishAskOrder, FormToPublishBidOrder
from django.contrib import messages
import pymongo
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

personalClientMdB = pymongo.MongoClient("mongodb://localhost:27017/")
myMngDb = personalClientMdB.get_database("db_btc_platform")


@login_required()
def publishBidOrder(request):
    sell_onOrderBook = SellOrder.objects.filter().order_by('-publication_time')
    loggedCustoumer = Customer.objects.get(user=request.user)

    if request.method == 'POST':
        form = FormToPublishBidOrder(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = loggedCustoumer
            buy_quantity = form.quantity
            buy_price = form.price

            if buy_quantity <= 0.0 or buy_price <= 0.0:
                messages.error(
                    request, 'Non puoi inserire quantità o prezzi negativi o nulli')
                return redirect('/publishBidOrder/')

            if loggedCustoumer.dollar_wallet >= buy_price and loggedCustoumer.dollar_wallet > 0:
                if sell_onOrderBook.count() == 0:
                    order_instance = BuyOrder(
                        associated_customer=loggedCustoumer, price=buy_price, quantity=buy_quantity)
                    loggedCustoumer.dollar_wallet -= float(buy_price)
                    order_instance.save()
                    loggedCustoumer.save()
                    messages.error(
                        request, "Ordine di acquisto inserito in waiting list in quanto non ci sono attualmente offerte di BTC")
                    return redirect('/')
                else:
                    for order in sell_onOrderBook:
                        if buy_price >= order.price and buy_quantity == order.quantity:  # --#

                            loggedCustoumer.dollar_wallet -= float(buy_price)
                            loggedCustoumer.btc_wallet += float(buy_quantity)
                            userSelling = order.associated_customer
                            # perchè la quantità era già stata frizata in fase di piazzemento ordine
                            userSelling.btc_wallet = userSelling.btc_wallet
                            userSelling.dollar_wallet += float(buy_price)
                            userSelling.profit += float(buy_price)
                            loggedCustoumer.profit -= float(buy_price)
                            loggedCustoumer.save()
                            userSelling.save()
                            messages.success(
                                request, 'Trovata corrispondenza prezzo su OrderBook vendite BTC! Esecuzione registazione transazione ')

                            firstTransCollect = myMngDb['Transactions Orders coinciding in quantity and price buyer side']
                            saveBuyTransaction = {

                                'Id User Selling': order.associated_customer.user.pk,
                                'User selling his btc': order.associated_customer.user.username,
                                'Pre-sale $ balance of selling User': order.associated_customer.dollar_wallet - buy_price,
                                'Post-sale $ balance of selling User': order.associated_customer.dollar_wallet,
                                'Post-sale BTC balance of selling User': order.associated_customer.btc_wallet,
                                'Pre-sale BTC balance of selling User ': order.associated_customer.btc_wallet + buy_quantity,

                                'Order quantity': buy_quantity,
                                'Order price': buy_price,

                                'Id User that buy': loggedCustoumer.user.pk,
                                'User that buy Btc': loggedCustoumer.user.username,
                                'Pre-sale $ balance of User that buy Btc': loggedCustoumer.dollar_wallet + buy_price,
                                'Post-sale $ balance of User that buy Btc': loggedCustoumer.dollar_wallet,
                                'Post-sale BTC balanceof User that buy Btc': loggedCustoumer.btc_wallet,
                                'Pre-sale BTC balance of User that buy Btc ': loggedCustoumer.btc_wallet - buy_quantity,
                            }
                            saveOne = firstTransCollect.insert_one(
                                saveBuyTransaction)
                            order.delete()
                            return redirect('/publishBidOrder/')  # --#

                        if buy_price >= order.price and buy_quantity != order.quantity:
                            if order.quantity >= buy_quantity:
                                loggedCustoumer.dollar_wallet -= float(
                                    buy_price)
                                loggedCustoumer.btc_wallet += float(
                                    order.quantity)

                                userSelling = order.associated_customer
                                # perchè la quantità era già stata frizata in fase di piazzemento ordine
                                userSelling.btc_wallet = userSelling.btc_wallet
                                userSelling.dollar_wallet += float(buy_price)
                                userSelling.profit += float(buy_price)
                                loggedCustoumer.profit -= float(buy_price)
                                loggedCustoumer.save()
                                userSelling.save()

                                messages.success(
                                    request, 'Trovata corrispondenza maggiormente favorevole in rapporto quantità_prezzo su OrderBook vendite BTC!! Esecuzione registazione transazione ')
                                secondTransCollect = myMngDb['Favorable transactions buyer side']

                                saveBuyTransaction = {

                                    'Id User Selling': order.associated_customer.user.pk,
                                    'User selling his btc': order.associated_customer.user.username,
                                    'Pre-sale $ balance of selling User': order.associated_customer.dollar_wallet - buy_price,
                                    'Post-sale $ balance of selling User': order.associated_customer.dollar_wallet,
                                    'Post-sale BTC balance of selling User': order.associated_customer.btc_wallet,
                                    'Pre-sale BTC balance of selling User ': order.associated_customer.btc_wallet + buy_quantity,

                                    'Order quantity': buy_quantity,
                                    'Order price': buy_price,

                                    'Id User that buy': loggedCustoumer.user.pk,
                                    'User that buy Btc': loggedCustoumer.user.username,
                                    'Pre-sale $ balance of User that buy Btc': loggedCustoumer.dollar_wallet + buy_price,
                                    'Post-sale $ balance of User that buy Btc': loggedCustoumer.dollar_wallet,
                                    'Post-sale BTC balanceof User that buy Btc': loggedCustoumer.btc_wallet,
                                    'Pre-sale BTC balance of User that buy Btc ': loggedCustoumer.btc_wallet - buy_quantity,
                                }
                                saveOne = secondTransCollect.insert_one(
                                    saveBuyTransaction)
                                order.delete()
                                return redirect('/publishBidOrder/')

                            else:
                                order_instance = BuyOrder(
                                    associated_customer=loggedCustoumer, price=buy_price, quantity=buy_quantity)
                                loggedCustoumer.dollar_wallet -= float(
                                    buy_price)
                                order_instance.save()
                                loggedCustoumer.save()
                                messages.error(
                                    request, "Ordine di acquisto inserito in waiting list in quanto, a parità di prezzo, vi sono vendite che offrono minori quantità BTC!")
                                return redirect('/')

                        else:
                            ##
                            order_instance = BuyOrder(
                                associated_customer=loggedCustoumer, price=buy_price, quantity=buy_quantity)
                            loggedCustoumer.dollar_wallet -= float(buy_price)
                            order_instance.save()
                            loggedCustoumer.save()
                            ##
                            messages.error(
                                request, "Ordine di acquisto inserito in waiting list ")
                            return redirect('/')

            else:
                messages.error(
                    request, 'Non hai sufficienti fondi per piazzare questo ordine ')
                return redirect('/publishBidOrder/')

    else:
        form = FormToPublishBidOrder()
        context = {'form': form}
        return render(request, 'order_buy_page.html', context)


@login_required()
def publishAskOrder(request):
    buy_onOrderBook = BuyOrder.objects.filter().order_by('-publication_time')
    loggedCustoumer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        form = FormToPublishAskOrder(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = loggedCustoumer
            sell_quantity = form.quantity
            sell_price = form.price

            if sell_quantity <= 0.0 or sell_price <= 0.0:
                messages.error(
                    request, 'Non puoi inserire quantità o prezzi negativi o nulli')
                return redirect('/publishAskOrder/')

            if loggedCustoumer.btc_wallet >= sell_quantity and loggedCustoumer.btc_wallet > 0.0:
                if buy_onOrderBook.count() == 0:
                    order_instance = SellOrder(
                        associated_customer=loggedCustoumer, price=sell_price, quantity=sell_quantity)
                    loggedCustoumer.btc_wallet -= float(sell_quantity)
                    order_instance.save()
                    loggedCustoumer.save()
                    messages.error(
                        request, "Ordine di vendita inserito in waiting list in quanto non ci sono attualmente proposte acquisto BTC")
                    return redirect('/')
                else:
                    for order in buy_onOrderBook:
                        if sell_quantity == order.quantity and sell_price <= order.price:  # --#

                            # --++++ #
                            loggedCustoumer.btc_wallet -= float(sell_quantity)
                            loggedCustoumer.dollar_wallet += float(sell_price)
                            buyingUser = order.associated_customer
                            # perchè la quantità era già stata frizata in fase di piazzemento ordine
                            buyingUser.dollar_wallet = buyingUser.dollar_wallet
                            buyingUser.btc_wallet += float(sell_quantity)
                            loggedCustoumer.profit += float(sell_price)
                            buyingUser.profit -= float(sell_price)
                            loggedCustoumer.save()
                            buyingUser.save()
                            messages.success(
                                request, 'Trovata corrispondenza prezzo su OrderBook acquisti BTC! Esecuzione registazione transazione ')
                            thirdTransCollect = myMngDb['Transactions Orders coinciding in quantity and price selling side']
                            saveSellTransaction = {

                                'Id User buying': order.associated_customer.user.pk,
                                'User buying btc': order.associated_customer.user.username,
                                'Pre-buy $ balance of buying User': order.associated_customer.dollar_wallet + sell_price,
                                'Post-buy $ balance of buying User': order.associated_customer.dollar_wallet,
                                'Post-buy BTC balance of buying User': order.associated_customer.btc_wallet,
                                'Pre-buy BTC balance of buying User ': order.associated_customer.btc_wallet - sell_quantity,

                                'Order quantity': sell_quantity,
                                'Order price': sell_price,

                                'Id User that sell': loggedCustoumer.user.pk,
                                'User that sell his Btc': loggedCustoumer.user.username,
                                'Pre-buy $ balance of selling User': loggedCustoumer.dollar_wallet - sell_price,
                                'Post-buy $ balance of selling User': loggedCustoumer.dollar_wallet,
                                'Post-buy BTC balance of selling User': loggedCustoumer.btc_wallet,
                                'Pre-buy BTC balance of selling User ': loggedCustoumer.btc_wallet + sell_quantity,

                            }
                            saveOne = thirdTransCollect.insert_one(
                                saveSellTransaction)
                            order.delete()
                            return redirect('/publishAskOrder/')

                        if sell_price <= order.price and sell_quantity != order.quantity:
                            if order.quantity <= sell_quantity:

                                # --++++ #
                                loggedCustoumer.dollar_wallet += float(
                                    sell_price)
                                loggedCustoumer.btc_wallet -= float(
                                    order.quantity)

                                userBuying = order.associated_customer
                                # perchè la quantità era già stata frizata in fase di piazzemento ordine
                                userBuying.dollar_wallet = userBuying.dollar_wallet
                                userBuying.btc_wallet += float(order.quantity)
                                userBuying.profit -= float(sell_price)
                                loggedCustoumer.profit += float(sell_price)

                                loggedCustoumer.save()
                                userBuying.save()

                                messages.success(
                                    request, 'Trovata corrispondenza favorevole in vendita in quanto a parità di prezzo l acquirente è disposto a recepisce una minor quantità di BTC !! Esecuzione registazione transazione ')

                                fourthTransCollect = myMngDb['Favorable transactions Selling side']

                                saveSellTransaction = {

                                    'Id User buying': order.associated_customer.user.pk,
                                    'User buying btc': order.associated_customer.user.username,
                                    'Pre-buy $ balance of buying User': order.associated_customer.dollar_wallet + sell_price,
                                    'Post-buy $ balance of buying User': order.associated_customer.dollar_wallet,
                                    'Post-buy BTC balance of buying User': order.associated_customer.btc_wallet,
                                    'Pre-buy BTC balance of buying User ': order.associated_customer.btc_wallet - sell_quantity,

                                    'Order quantity': sell_quantity,
                                    'Order price': sell_price,

                                    'Id User that sell': loggedCustoumer.user.pk,
                                    'User that sell his Btc': loggedCustoumer.user.username,
                                    'Pre-buy $ balance of selling User': loggedCustoumer.dollar_wallet - sell_price,
                                    'Post-buy $ balance of selling User': loggedCustoumer.dollar_wallet,
                                    'Post-buy BTC balance of selling User': loggedCustoumer.btc_wallet,
                                    'Pre-buy BTC balance of selling User ': loggedCustoumer.btc_wallet + sell_quantity,

                                }
                                saveOne = fourthTransCollect.insert_one(
                                    saveSellTransaction)
                                order.delete()
                                return redirect('/publishAskOrder/')
                            else:
                                order_instance = SellOrder(
                                    associated_customer=loggedCustoumer, price=sell_price, quantity=sell_quantity)
                                loggedCustoumer.btc_wallet -= float(
                                    sell_quantity)
                                order_instance.save()
                                loggedCustoumer.save()
                                messages.error(
                                    request, "Ordine di vendita inserito in waiting list in quanto, a parità di prezzo, gli acquirenti vorrebbero una maggior quantità di BTC!")
                                return redirect('/')

                        else:
                            order_instance = SellOrder(
                                associated_customer=loggedCustoumer, price=sell_price, quantity=sell_quantity)
                            loggedCustoumer.btc_wallet -= float(sell_quantity)

                            order_instance.save()
                            loggedCustoumer.save()
                            messages.error(
                                request, "Ordine di vendita inserito in waiting list ")
                            return redirect('/')
            else:
                messages.error(
                    request, 'Il tuo wallet non dispone della quantità di BTC indicata ')
                return redirect('/publishAskOrder/')
    else:
        form = FormToPublishAskOrder()
        context = {'form': form}
        return render(request, 'order_sell_page.html', context)


@login_required()
def activBuyOrders(request, singleOrAll):
    response = []
    try:
        current_customer = Customer.objects.get(user=request.user)
        if singleOrAll == "single":
            buy_onOrderBook = BuyOrder.objects.filter(
                associated_customer=current_customer).order_by('-publication_time')
        elif singleOrAll == "all":
            buy_onOrderBook = BuyOrder.objects.filter().order_by('-publication_time')
        for order in buy_onOrderBook:
            response.append(
                {
                    "id_order": f"{order.id}",
                    "user": f"{order.associated_customer.user.username}",
                    "price": f"{order.price}",
                    "quantity": f"{order.quantity}",
                    "publication_time": f"{order.publication_time}",
                }
            )
        return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})
    except ObjectDoesNotExist:  # per gestire l'eccezione dell'Admin iniziale creato da Terminale
        buy_onOrderBook = BuyOrder.objects.filter().order_by('-publication_time')
        for order in buy_onOrderBook:
            response.append(
                {
                    "id_order": f"{order.id}",
                    "user": f"{order.associated_customer.user.username}",
                    "price": f"{order.price}",
                    "quantity": f"{order.quantity}",
                    "publication_time": f"{order.publication_time}",
                }
            )
        return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})


@login_required()
def activSellOrders(request, singleOrAll):
    response = []
    try:
        current_customer = Customer.objects.get(user=request.user)
        if singleOrAll == "single":
            sell_onOrderBook = SellOrder.objects.filter(
                associated_customer=current_customer).order_by('-publication_time')
        elif singleOrAll == "all":
            sell_onOrderBook = SellOrder.objects.filter().order_by('-publication_time')
        for order in sell_onOrderBook:
            response.append(
                {
                    "id_order": f"{order.id}",
                    "user": f"{order.associated_customer.user.username}",
                    "price": f"{order.price}",
                    "quantity": f"{order.quantity}",
                    "publication_time": f"{order.publication_time}",
                }
            )
            return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})
    except ObjectDoesNotExist:
        sell_onOrderBook = SellOrder.objects.filter().order_by('-publication_time')
        for order in sell_onOrderBook:
            response.append(
                {
                    "id_order": f"{order.id}",
                    "user": f"{order.associated_customer.user.username}",
                    "price": f"{order.price}",
                    "quantity": f"{order.quantity}",
                    "publication_time": f"{order.publication_time}",
                }
            )
        return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

######


@staff_member_required()
def profitsOrLoss(request):
    customers = Customer.objects.all()
    response = []
    for client in customers:
        try:
            response.append(
                {
                    "User": f"{client.user.username}",
                    "Total Profit": f"{client.profit}",
                }
            )
        except:
            response.append(
                {
                    "User": "None",
                    "Total Profit": "None",
                }
            )
    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

######


@login_required()
def exportJsonByCollectionMdb(request, choose_export):
    mycol = myMngDb.get_collection(choose_export)
    mydoc = mycol.find()
    response = []

    if choose_export not in ["Favorable transactions buyer side", "Transactions Orders coinciding in quantity and price buyer side", "Transactions Orders coinciding in quantity and price selling side", "Favorable transactions Selling side"]:
        messages.error(request, 'Scelta non valida!')
        return redirect('/')

    if choose_export == 'Favorable transactions buyer side':
        for r in mydoc:
            response.append(
                {
                    'Id User Selling': r['Id User Selling'],
                    'User selling his btc': r['User selling his btc'],
                    'Pre-sale $ balance of selling User': r['Pre-sale $ balance of selling User'],
                    'Post-sale $ balance of selling User': r['Post-sale $ balance of selling User'],
                    'Post-sale BTC balance of selling User': r['Post-sale BTC balance of selling User'],
                    'Pre-sale BTC balance of selling User ': r['Pre-sale BTC balance of selling User '],

                    'Order quantity': r['Order quantity'],
                    'Order price': r['Order price'],

                    'Id User that buy': r['Id User that buy'],
                    'User that buy Btc': r['User that buy Btc'],
                    'Pre-sale $ balance of User that buy Btc': r['Pre-sale $ balance of User that buy Btc'],
                    'Post-sale $ balance of User that buy Btc': r['Post-sale $ balance of User that buy Btc'],
                    'Post-sale BTC balanceof User that buy Btc': r['Post-sale BTC balanceof User that buy Btc'],
                    'Pre-sale BTC balance of User that buy Btc ': r['Pre-sale BTC balance of User that buy Btc '],
                }
            )
    elif choose_export == 'Transactions Orders coinciding in quantity and price buyer side':
        for r in mydoc:
            response.append(
                {
                    'Id User Selling': r['Id User Selling'],
                    'User selling his btc': r['User selling his btc'],
                    'Pre-sale $ balance of selling User': r['Pre-sale $ balance of selling User'],
                    'Post-sale $ balance of selling User': r['Post-sale $ balance of selling User'],
                    'Post-sale BTC balance of selling User': r['Post-sale BTC balance of selling User'],
                    'Pre-sale BTC balance of selling User': r['Pre-sale BTC balance of selling User '],

                    'Order quantity': r['Order quantity'],
                    'Order price': r['Order price'],

                    'Id User that buy': r['Id User that buy'],
                    'User that buy Btc': r['User that buy Btc'],
                    'Pre-sale $ balance of User that buy Btc': r['Pre-sale $ balance of User that buy Btc'],
                    'Post-sale $ balance of User that buy Btc': r['Post-sale $ balance of User that buy Btc'],
                    'Post-sale BTC balanceof User that buy Btc': r['Post-sale BTC balanceof User that buy Btc'],
                    'Pre-sale BTC balance of User that buy Btc': r['Pre-sale BTC balance of User that buy Btc '],
                }
            )
    elif choose_export == 'Transactions Orders coinciding in quantity and price selling side':
        for r in mydoc:
            response.append(
                {
                    'Id User buying': r['Id User buying'],
                    'User buying btc': r['User buying btc'],
                    'Pre-buy $ balance of buying User': r['Pre-buy $ balance of buying User'],
                    'Post-buy $ balance of buying User': r['Post-buy $ balance of buying User'],
                    'Post-buy BTC balance of buying User': r['Post-buy BTC balance of buying User'],
                    'Pre-buy BTC balance of buying User ': r['Pre-buy BTC balance of buying User '],

                    'Order quantity': r['Order quantity'],
                    'Order price': r['Order price'],

                    'Id User that sell': r['Id User that sell'],
                    'User that sell his Btc': r['User that sell his Btc'],
                    'Pre-buy $ balance of selling User': r['Pre-buy $ balance of selling User'],
                    'Post-buy $ balance of selling User': r['Post-buy $ balance of selling User'],
                    'Post-buy BTC balance of selling User': r['Post-buy BTC balance of selling User'],
                    'Pre-buy BTC balance of selling User ': r['Pre-buy BTC balance of selling User '],

                }
            )
    elif choose_export == 'Favorable transactions Selling side':
        for r in mydoc:
            response.append(
                {
                    'Id User buying': r['Id User buying'],
                    'User buying btc': r['User buying btc'],
                    'Pre-buy $ balance of buying User': r['Pre-buy $ balance of buying User'],
                    'Post-buy $ balance of buying User': r['Post-buy $ balance of buying User'],
                    'Post-buy BTC balance of buying User': r['Post-buy BTC balance of buying User'],
                    'Pre-buy BTC balance of buying User ': r['Pre-buy BTC balance of buying User '],

                    'Order quantity': r['Order quantity'],
                    'Order price': r['Order price'],

                    'Id User that sell': r['Id User that sell'],
                    'User that sell his Btc': r['User that sell his Btc'],
                    'Pre-buy $ balance of selling User': r['Pre-buy $ balance of selling User'],
                    'Post-buy $ balance of selling User': r['Post-buy $ balance of selling User'],
                    'Post-buy BTC balance of selling User': r['Post-buy BTC balance of selling User'],
                    'Pre-buy BTC balance of selling User ': r['Pre-buy BTC balance of selling User '],
                }
            )

    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})
