import os
import sys
import requests
import urllib.request
import time
import datetime
import threading
from lxml import html

class stonks:
    def __init__(self):
        self.url = "https://markets.businessinsider.com"
        self.indeces = ["/index/components/dow_jones", 
            "/index/components/s&p_500",
            "/index/components/nasdaq_100",
            "/index/components/ftse_100",
            "/index/components/euro_stoxx_50",
            "/index/components/dax"]
        self.companies = []
        self.company_indicator = "/stocks/"
        self.company_links_path = sys.path[0] + "\\company_links.dat"

        self.price_key = '"price":'
        self.stock_start = "/stock/"
        self.stock_end = "-stock"
        
    def start(self):
        #see if company file list already exists
        if not os.path.isfile(self.company_links_path):
            self.update_companies_file()
        else:
            #Set the companies list to most up-to-date file
            self.companies = [line.rstrip('\n') for line in open(self.company_links_path, 'r')]
        print(len(self.companies))

    def update_companies_file(self):
        #Get a list of available companies
        for index in self.indeces:
            index_url = self.url + index
            page = requests.get(index_url)
            webpage = html.fromstring(page.content)

            #For every link, check if starts with same indicator for stocks.
            #If unique, append
            for link in webpage.xpath('//a/@href'):
                if link.startswith(self.company_indicator) and not link in companies:
                    self.companies.append(link)
            with open("company_links.dat", "w") as file:
                for company in self.companies:
                    file.write(company + "\n")

    #Get the prices                    
    def get_prices(self):
        start_time = time.time()
        prices = []

        for company in self.companies[0:20]:
            try:
                company_info = urllib.request.urlopen(self.url+company).read().decode('UTF-8')
                price_index = company_info.find(self.price_key)
                price = company_info[price_index + len(self.price_key):company_info.find(",", price_index + len(self.price_key))]
                price = price.replace('"', "")
                stock_name = company[len(self.stock_start) + 1:len(company)-len(self.stock_end)]
                prices.append([stock_name, price, datetime.datetime.now()])
                print(price)
            except:
                continue
            
        #Print times
        print("\n\n\nEND:")
        print("--- %s seconds ---" % (time.time() - start_time))

        #Now save the data
        save_thread = threading.Thread(target=self.save_data, args=(prices,))
        save_thread.start()
        
    def save_data(self, prices):
        with open("data.dat", "w") as file:
            for price in prices:
                file.write(price[0] + ":" + str(price[1]) + ", " + str(price[2]) + "\n")

if __name__ == '__main__':
    stonks = stonks()
    stonks.start()
    stonks.get_prices()
    
