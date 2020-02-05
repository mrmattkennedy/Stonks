import os
import sys
import requests
import urllib.request
import time
from lxml import html

url = "https://markets.businessinsider.com"
indeces = ["/index/components/dow_jones", 
    "/index/components/s&p_500",
    "/index/components/nasdaq_100",
    "/index/components/ftse_100",
    "/index/components/euro_stoxx_50",
    "/index/components/dax"]
companies = []

#see if company file list already exists
company_links_path = sys.path[0] + "\\company_links.dat"

#Get a list of available stocks
if not os.path.isfile(company_links_path):
    print("not skipping")
    for index in indeces:
        index_url = url + index
        page = requests.get(index_url)
        webpage = html.fromstring(page.content)
        
        for link in webpage.xpath('//a/@href'):
            if link.startswith("/stocks/") and not link in companies:
                companies.append(link)
        with open("company_links.dat", "w") as file:
            for company in companies:
                file.write(company + "\n")

#Set the companies list to most up-to-date file
companies = [line.rstrip('\n') for line in open(company_links_path, 'r')]

#Get the prices
price_key = '"price":'
stock_start = "/stock/"
stock_end = "-stock"
start_time = time.time()
prices = []

for company in companies[0:20]:
    try:
        company_info = urllib.request.urlopen(url+company).read().decode('UTF-8')
        price_index = company_info.find(price_key)
        price = company_info[price_index + len(price_key):company_info.find(",", price_index + len(price_key))]
        price = price.replace('"', "")
        stock_name = company[len(stock_start) + 1:len(company)-len(stock_end)]
        prices.append([stock_name, price])
    except:
        continue

print("\n\n\nEND:")
print("--- %s seconds ---" % (time.time() - start_time))
