import os
import sys
import csv
import requests
import urllib.request
import time
import datetime
import threading
from lxml import html

class stonks_scraper:
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
        self.company_links_path = sys.path[0] + "\\data\\company_links.dat"
        self.prices_links_path = sys.path[0] + "\\data\\data.csv"

        self.price_key = '"price":'
        self.stock_start = "/stock/"
        self.stock_end = "-stock"

        self.iteration_count = 1
        
    def start(self):
        #see if company file list already exists
        if not os.path.isfile(self.company_links_path):
            self.update_companies_file()
        else:
            #Set the companies list to most up-to-date file
            self.companies = [line.rstrip('\n') for line in open(self.company_links_path, 'r')]

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
    def get_prices(self, messageQ=None):
        start_time = time.time()
        prices = []

        for company in self.companies:
            try:
                company_info = urllib.request.urlopen(self.url+company).read().decode('UTF-8')
                price_index = company_info.find(self.price_key)
                price = company_info[price_index + len(self.price_key):company_info.find(",", price_index + len(self.price_key))]
                price = price.replace('"', "")
                if not self.is_number(price):
                    continue
                stock_name = company[len(self.stock_start) + 1:len(company)-len(self.stock_end)]
                prices.append([stock_name, price, datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")])
                #print(stock_name + ":" + str(price))
            except:
                continue

        #Now save the data
        save_thread = threading.Thread(target=self.save_data, args=(prices,))
        save_thread.start()
        
        if messageQ:
            messageQ.put(self.iteration_count)        
            messageQ.put(round(time.time() - start_time, 2))
            
        self.iteration_count+=1

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def save_data(self, prices):
        #Create file if it doesn't exist
        if not os.path.isfile(self.prices_links_path):
            open(self.prices_links_path, "w").close()
        
        with open(self.prices_links_path, "r+") as file:
            data_reader = csv.reader(file, delimiter=',')
            data_contents = [row for row in data_reader]
            
            #Step 1: See if company exists. If not, add at the end.
            #Step 2: Append data at the right spot in a row.
            #Step 3: Save data
            for price in prices:
                company = price[0]
                cost = price[1]
                time = price[2]

                #Step 1
                if len(data_contents) > 0:
                    if company not in data_contents[0]:
                        data_contents[0].extend([company, "",])
                        for row in data_contents[1:]:
                            row.extend(["", ""])
                else:
                    data_contents.append([company, "",])
                    
                #Step 2
                #Get index of company, that column is the price, col+1 is time stamp.
                #Get first empty value in column and insert there.
                #CSV is always a rectangle, so no issues on elements not existing.
                #If get to bottom, add an entire row
                company_index = data_contents[0].index(company)
                column_data = data_contents[0][company_index]
                empty_row = 0
                try:
                    while column_data:
                        empty_row += 1
                        column_data = data_contents[empty_row][company_index]
                except IndexError:
                    data_contents.append(["" for column in data_contents[0]])
                    
                data_contents[empty_row][company_index] += str(cost)
                data_contents[empty_row][company_index+1] += str(time)

            #Step 3
            file.seek(0)
            for row in data_contents:
                line = ",".join(row)
                file.write(line + "\n")                    
            file.truncate()

        return

#If running standalone
if __name__ == '__main__':
    stonks = stonks_scraper()
    stonks.start()
    count = 1
    while True:
        stonks.get_prices()
        print("Iteration %d done!\n\n" %(count))
        count+=1
    
