# ProgettoMongoDBdiAntoninoPaterno
{deploy address: https://github.com/antopat1/ProgettoMongoDBdiAntoninoPaterno & AwS http://cryptoplatform.sytes.net ( http://13.37.18.60:8000 ) }


Piattaforma scambio bitcoin

-Utilizzando l’IDE PyCharm ed avvalendosi della distribuzione PyMongo all’interno framework Django per 
l’archiviazione documentale su database non SQL MongoDb, si è realizzato una piattaforma di scambio 
che consente di piazzare ordini di acquisto e ordini di vendita con relativi dettagli transazionali

- Ad ogni nuovo utente che si registra alla piattaforma attribuisce un quantità di bitcoin variabile tra 1 e 10
Sfruttando un interrogazione API al sito CoinMarketCap, viene automatizzato l’aggiornamento al valore corrente di Btc

Views funzionali disponibili per USER STANDARD

-  Dalla tipica pagina di registrazione Utente o a seguito della fase di login si accede alla Home Page che , oltre 
al saldo in BTC e Dollari , mostra profitto o perdita rispetto alla posizione inizialmente attribuita in modo 
arbitrario dalla piattaforma nonché gli ordini di acquisto e vendita attualmente presenti sulla stessa

- Dalla tipica pagina di registrazione Utente o a seguito della fase di login si accede alla Home Page che , oltre 
al saldo in BTC e Dollari , mostra profitto o perdita rispetto alla posizione inizialmente attribuita in modo 
arbitrario dalla piattaforma nonché gli ordini di acquisto e vendita attualmente presenti sulla stessa.

 In corrispondenza di ciascun OrderBook sarà possibile per l’utente 
 
- Pizzare un nuovo ordine
- Estrarre un Json dei propri ordini
- Visualizzare il dettagli degli stessi per modificare o cancellare degli ordini in base allo specifico ID

•  Se ad accedere alla piattaforma è un superuser , non si avrà la possibilità di piazzare ordini ma di eseguire 
delle interrogazioni riguardanti la totalità degli utenti 

 • Il superUser potrà
 - Estrarre un Json di tutti gli ordini attivi in acquisto e vendita
- Visualizzare il dettagli degli stessi per cancellare degli ordini in base allo specifico ID
- Estrarre profitto o perdita di ciascun utente.
-Mostrare i dati di Collection MongoDb create in fase di match tra domanda ed offerta nel momento in cui 
una transazione viene realizzata


