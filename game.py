### Steam


import json
import requests
from bs4 import BeautifulSoup
import time
from flask import Flask, render_template, request
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

CACHE_FILENAME = 'cache.json'
cache_dict = {}

def open_cache():
    ''' opens cache file if it exists and loads the JSON into the cache_dict
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 
 
def get_html_check_cache(url, cache):
    '''Check the cache if there are saved results for the url. It there are, return those.
    If not, send a request to the url, save it to cache, and return it
    
    Parameters
    ----------
    url: string
        The URL for the game searched results
    cache: 
        dict to store data
    
    Returns
    -------
    dict
        cache, JSON
    '''
    if (url in cache.keys()):
        print("Result fetching from cache")
        return cache[url]
    else:
        print("Result fetching from URL")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def get_html_check_cache_epic(url, cache):
    '''Check the cache if there are saved results for the url. It there are, return those.
    If not, send a request to the url, save it to cache, and return it
    
    Parameters
    ----------
    url: string
        The URL for the game searched results
    cache: 
        dict to store data
    
    Returns
    -------
    dict
        cache, JSON
    '''
    if (url in cache.keys()):
        print("Result fetching from cache")
        return cache[url]
    else:
        print("Result fetching from URL")
        time.sleep(1)
        chromeOptions = webdriver.ChromeOptions() 
        # chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
        # chromeOptions.add_argument("--no-sandbox") 
        # chromeOptions.add_argument("--disable-setuid-sandbox") 

        # chromeOptions.add_argument("--remote-debugging-port=9222")  # this

        # chromeOptions.add_argument("--disable-dev-shm-using") 
        # chromeOptions.add_argument("--disable-extensions") 
        # chromeOptions.add_argument("--disable-gpu") 
        # chromeOptions.add_argument("start-maximized") 
        # chromeOptions.add_argument("disable-infobars")
        # chromeOptions.add_argument(r"user-data-dir=.\cookies\\test") 
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chromeOptions)
        driver.get(url)
        
        titles = driver.find_elements(By.CLASS_NAME, 'css-15fmxgh')
        titles_list = []
        original_price_list = []
        discount_price_list = []
        if titles == None:
            titles_list = []
            original_price_list = []
            discount_price_list = []
        else:
            for t in range(len(titles)):
                titles_list.append(titles[t].text.split('\n')[1])
                if len(titles[t].text.split('$')) == 1: # Free or Coming Soon
                    original_price_list.append('None')
                    discount_price_list.append('None')
                elif len(titles[t].text.split('$')) == 2: # No discount
                    original_price_list.append(titles[t].text.split('$')[-1])
                    discount_price_list.append(titles[t].text.split('$')[-1])
                elif len(titles[t].text.split('$')) == 3: # Discount
                    original_price_list.append(titles[t].text.split('$')[1][:-1])
                    discount_price_list.append(titles[t].text.split('$')[-1])

        cache[url] = titles_list + original_price_list + discount_price_list
        save_cache(cache)
        return cache[url]
    
def search_results_steam(search_term):
    url = 'https://store.steampowered.com/search/?term=' + search_term + '&category1=998'
    html_text = get_html_check_cache(url, cache_dict)
    soup = BeautifulSoup(html_text, 'html.parser')
    results = soup.find(id='search_results')
    if results == None:
        return None
    else:
        game_result = []
        game_list = results.find_all('a')
        for game in game_list:
            game_dict = {}
            #appid for each game
            if 'data-ds-appid' not in game.attrs.keys():
                continue
            else:
                game_dict['appid'] = game.attrs['data-ds-appid']
            
            #game title
            game_dict['title'] = game.find(class_='title').text

            #game release date
            game_dict['release_date'] = game.find(class_='search_released').text

            #game review
            game_review = game.find(class_='search_reviewscore').find(class_='search_review_summary')
            if game_review == None:
                game_dict['review'] = 'None'
                game_dict['score'] = 'None'
                game_dict['reviewer_num'] = 'None'
            else:
                game_dict['review'] = game_review.attrs['data-tooltip-html'].split('<br>')[0]
                game_dict['score'] = game_review.attrs['data-tooltip-html'].split('<br>')[1].split(' ')[0]
                game_dict['reviewer_num'] = game_review.attrs['data-tooltip-html'].split('<br>')[1].split(' ')[3]

            game_price = game.find(class_='search_price').text.strip()
            if game_price == None or game_price == '':
                game_dict['original_price'] = 'None'
                game_dict['discount_price'] = 'None'
            elif game_price == "Free" or game_price == "Free to Play" or game_price == "Free To Play":
                game_dict['original_price'] = '0'
                game_dict['discount_price'] = '0'
            else:
                game_dict['original_price'] = game_price.split('$')[1]
                game_dict['discount_price'] = game_price.split('$')[-1]
            game_result.append(game_dict)
    return game_result

def search_results_epic(search_term):
    url = 'https://store.epicgames.com/en-US/browse?q='+search_term+'&sortBy=relevancy&sortDir=DESC&category=Game&count=40&start=0'
    game_info = get_html_check_cache_epic(url, cache_dict)
    list_size = int(len(game_info)/3)
    titles_list = game_info[0:list_size]
    original_price_list = game_info[list_size:2*list_size]
    discount_price_list = game_info[2*list_size:3*list_size]
    return titles_list, original_price_list, discount_price_list

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') # First page to search for the games

@app.route('/result', methods=['POST'])
def result():
    search_term = request.form["search_term"]
    results_steam = search_results_steam(search_term)
    if len(results_steam)==0:
        return render_template('noresult.html')
    else:
        titles_list_epic, original_price_list_epic, discount_price_list_epic = search_results_epic(search_term)
        game_num = int(request.form["game_num"])
        results_steam_final = []
        results_epic_final = []

        minimum_len = min(len(titles_list_epic), len(results_steam))

        if int(game_num) > minimum_len:
            for i in range(minimum_len):
                results_steam_final.append([results_steam[i]['title'], results_steam[i]['original_price'], results_steam[i]['discount_price']])
                results_epic_final.append([titles_list_epic[i], original_price_list_epic[i], discount_price_list_epic[i]])
            return render_template('result.html', results_steam_final = results_steam_final, results_epic_final = results_epic_final)
        else:
            for i in range(game_num):
                results_steam_final.append([results_steam[i]['title'], results_steam[i]['original_price'], results_steam[i]['discount_price']])
                results_epic_final.append([titles_list_epic[i], original_price_list_epic[i], discount_price_list_epic[i]])
            return render_template('result.html', results_steam_final = results_steam_final, results_epic_final = results_epic_final)

if __name__ == "__main__":
    cache_dict = open_cache()
    app.run(debug=True, use_reloader=False)
