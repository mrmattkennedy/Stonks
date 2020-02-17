import sys
import time
import math
import requests
import urllib.request
import threading
from string import whitespace
from pathlib import Path
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup
from string import ascii_uppercase

symbols = []
bad_symbols = []
rootDir = Path(sys.path[0]).parent
company_links_path = str(rootDir) + "\\data\\company_symbols.dat"
symbol_finder_url = 'http://eoddata.com/stocklist/NYSE/{}.htm'

def get_company_letter_links():
    for letter in ascii_uppercase:
        url = symbol_finder_url.format(letter)
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')
        table = soup.find("table", {"class": "quotes"})
        stocks = table.findAll("tr")

        token_start = 'onclick="location.href=' + "'/stockquote/NYSE/"
        token_end = ".htm'"
        #print(stocks[1])
        for stock in stocks[1:]:
            str_stock = str(stock)
            symbols.append(str_stock[str_stock.find(token_start) + len(token_start):
                                     str_stock.find(token_end)])
        print(letter)

def scrape_data(stock_list, startIndex):
    for stock in range(len(stock_list)):
        try:
            loop_time = time.time()
            
            text = urllib.request.urlopen(base.format(stock_list[stock])).read().decode('UTF-8')
            price_index = text.find(price_key)
            price = text[price_index + len(price_key):text.find(",", price_index + len(price_key))]
            price = price.replace(" ", '').replace('"', '')
            
            #print("{0}: {1}, {2}".format(stock_list[stock], price, round(time.time() - loop_time, 2)))
            try:
                float(price)
                symbol_data[stock + startIndex] = [stock_list[stock], price]
            except:
                print(stock_list[stock] + " not working")
                bad_symbols.append(stock_list[stock])
        except urllib.error.HTTPError:
            print(stock + " not found!")

def get_symbol_data():
    for symbol in symbols:
        scrape_data(symbol, 0)

def get_symbol_data_threaded():
    num_threads = 100
    thread_list = []
    start_time = time.time()
    for chunk in SplitList(companies, num_threads):
        startIndex = companies.index(chunk[0])
        scrape_thread = threading.Thread(target=scrape_data, args=(chunk,startIndex))
        thread_list.append(scrape_thread)
        scrape_thread.start()
    print("Active count is " + str(threading.active_count()))
    for thread in thread_list:
        thread.join()
    
    print("Total time: " + str(round(time.time() - start_time)))
    print(len(companies))
    for item in range(len(symbol_data)-1, 0, -1):
        if symbol_data[item] is None:
            del companies[item]
    print(len(companies))
    for bad in bad_symbols:
        print(bad + " index is " + companies.index(bad))
    #    print(str(companies.index(chunk[0])) + ", " + str(companies.index(chunk[-1]))) 
   # starting_index = [math.floor(company_len/num_threads) * i for i in range(len
    
def save_data():
    with open(company_links_path, "w") as file:
        for symbol in actual_symbols:
            file.write(symbol + "\n")
            
def SplitList(unsplitList, chunk_size):
    return [unsplitList[offs:offs+chunk_size] for offs in range(0, len(unsplitList), chunk_size)]

companies = [line.rstrip('\n') for line in open(company_links_path, 'r')]
company_len = len(companies)
symbol_data = [None] * company_len
#print(len(companies))
#get_company_letter_links()
#get_symbol_data()
#urllib.urlretrieve("http://www.example.com/test.html", "test.txt")
base = "https://markets.businessinsider.com/stocks/{}-stock"
price_key = '"price":'
count = 1
actual_symbols = []
get_symbol_data_threaded()
#print(time.time() - start_time)

