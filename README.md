# ProgettoMongoDBdiAntoninoPaterno

Bitcoin Exchange Platform

- Utilizing the PyCharm IDE and leveraging the PyMongo distribution within the Django framework for document storage on the NoSQL MongoDB database, a trading platform has been developed that allows users to place buy and sell orders with transactional details.

- Upon registration, each new user is assigned a variable amount of bitcoins between 1 and 10. Using an API query to the CoinMarketCap website, the current value of BTC is automatically updated.

Functional views available for STANDARD USERS:

- Upon typical user registration or after the login phase, users access the Home Page which displays their BTC and Dollar balances, as well as the profit or loss compared to the initially assigned position by the platform. It also shows the current buy and sell orders on the platform.

At each OrderBook, users can:

- Place a new order
- Extract a JSON of their orders
- View the details of their orders to modify or delete them based on the specific ID

• If a superuser accesses the platform, they will not be able to place orders but can perform queries regarding all users.

• The superuser can:

- Extract a JSON of all active buy and sell orders
- View the details of orders to delete them based on the specific ID
- Extract the profit or loss of each user
- Show the data of MongoDB collections created during the matching process between supply and demand when a transaction is realized.

