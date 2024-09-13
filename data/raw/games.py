import requests
import sys 
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import re

url = 'https://olympics.com/en/olympic-games'

s = requests.Session()

# many sites including this one reject requests with no http headers; typically only User-Agent is required
# you can copy these from any browser or use an agent from this list: https://deviceatlas.com/blog/list-of-user-agent-strings
s.headers =  { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0', 
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate',
               'Content-Type': 'text/plain',
               'Connection': 'keep-alive',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache',
               'TE': 'Trailers'
               }

print(url)
r = s.get(url)
content_str = str(r.content) # raw page html containing some urls we want

# in this case it is easier to parse the text directly rather than with beautifulsoup
hosts_str = content_str.split('itemListElement":')[1].split(']')[0] # grab the text between the two strings 'itemListElement":' and ']'
# ^ this is the section of html which contains the links we want to collect
urls_str = hosts_str.split('"url":"') # each url is preceded by this str
host_urls = []
for item in urls_str:
    if 'http' in item:
        host_urls.append(item.split('"')[0].split('/')[-1]) # truncate everything after the url and everything before the last slash

host_urls = host_urls[host_urls.index('paris-2024')+1:]
# remove the first few host countries of future games, also no results yet for paris

# print(host_urls) # the list of host countries to iterate over

df = pd.DataFrame(index=host_urls) # create df to store output, with host/year as index

browser = webdriver.Firefox() # selenium is useful for scraping sites with a lot of javascript or complex internal APIs, but it makes the script much slower and less reliable
for url in host_urls:
    results_url = 'https://olympics.com/en/olympic-games/' + url + '/results'
    print(results_url)
    browser.get(results_url)
    body = browser.find_element(By.TAG_NAME, 'html')
    body.click()
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    body.send_keys(Keys.PAGE_DOWN) # scroll to bottom of page
    html = browser.execute_script("return document.documentElement.outerHTML") # execute js on page
    
    soup = BeautifulSoup(html, 'lxml')
    
    all_links_soup = soup.find_all('a') # every url on the page
    
    for item in all_links_soup:
        if item.get('href'):
            if '/en/olympic-games/' + url + '/results/' in item.get('href'): # url points to results page for a given sport
                df.loc[url, item.get('href').split('/')[-1]] = True  # record that the sport was played the given year

df = df[sorted(df.columns)]
df.to_csv('games.csv', index=True)