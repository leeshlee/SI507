This is a search engine to search games in STEAM and EPIC GAMES to compare the prices between these two platforms.

README
Run the game.py file to activate the search engine, and it will lead you to a web page with your local host.
Enter the search term you want to search, and choose the number of games you want to see (1~10).
Then, it will show you the games titles and the original/discount prices for each game in STEAM and EPIC GAMES.
When first time searching, it will take some time and a chrome window will pop up and will close automatically for data scrapping.

PACKAGES
requests, bs4, flask, selenium, webdriver_manager

DATA STRUCTURE
The basic data structure is a dictionary structure. The whole URL will be the key for the cache. The searched results will be separated by each game.
For each game, a dictionary will be defined, and the features (such as titles, prices, reviews, etc.) that I’m interested will be the keys for the dictionary.
The exact information for each feature will be the value of the dictionary. Then, each dictionary will be saved back to the cache to be reused in the future.
