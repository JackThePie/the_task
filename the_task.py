"""Simple script to get data from IMDB and Steam"""

from requests import get
import const
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse as urlparse


def get_data():
    """
    Main function
    """
    whole_data = []
    for url in const.IMDB_URLS:
        # Get data about items using BeautifulSoup
        page = response_getter(url)
        data = imdb_data_getter(page)
        # Parse category and subcategory from URL
        parsed = urlparse.urlparse(url)
        category = urlparse.parse_qs(parsed.query)['title_type'][0]
        subcategory = urlparse.parse_qs(parsed.query)['genres'][0]
        for row in data:
            row.update({"category": category, 'subcategory': subcategory})
        whole_data.extend(data)

    for url in const.STEAM_URLS:
        # Get data about items using BeautifulSoup
        page = response_getter(url)
        data = steam_data_getter(page)
        # Set category and parse subcategory from URL
        category = 'game'
        subcategory = url.split("/")[-2].lower()
        for row in data:
            row.update({"category": category, 'subcategory': subcategory})
        whole_data.extend(data)
    # Put data into pandas DataFrame, clean-up and save to csv
    df = pd.DataFrame(whole_data)
    df = df.replace('feature', 'movie')
    df = df.replace('tv_series,mini_series', 'tv_series')
    df = df.replace('Free%20to%20Play', 'free%20to%20play')
    df.to_csv('results.csv', encoding='utf-8')


def response_getter(request):
    response = get(request, headers={'Accept-Language': 'en-US, en'})
    if response.status_code != 200:
        print('Request: {}; Status code: {}'.format(request, response.status_code))
    return BeautifulSoup(response.text, 'html.parser')


def imdb_data_getter(page):
    mv_containers = page.find_all('div', class_='lister-item mode-advanced')
    data = []
    for container in mv_containers:
        tmp_dir = {}
        name = container.h3.a.text
        tmp_dir['topic'] = name
        tail = container.h3.a['href']
        tmp_dir['url'] = 'https://www.imdb.com' + tail
        data.append(tmp_dir)
    return data


def steam_data_getter(page):
    data = []
    gm_containers = page.find_all('a', {'class': 'tab_item'})
    for container in gm_containers:
        tmp_dir = {}
        name = container.find('div', class_='tab_item_name').text
        tmp_dir['topic'] = name
        url = container['href']
        tmp_dir['url'] = url
        data.append(tmp_dir)
    return data


if __name__ == '__main__':
    get_data()