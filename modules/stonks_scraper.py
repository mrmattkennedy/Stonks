import os
import sys
import csv
import requests
import urllib.request
import time
import datetime
import threading
from bs4 import BeautifulSoup
from lxml import html
from pathlib import Path
from lxml import etree

class stonks_scraper:
    def __init__(self):
        self.quote_url = "https://markets.businessinsider.com/stocks/{}-stock"
        self.symbol_finder_url = 'https://swingtradebot.com/equities?page={}'
        self.symbol_lookup_end = 97 #last page is 96
        self.symbols = []
        self.symbol_data = []
        self.rootDir = Path(sys.path[0]).parent
        self.company_links_path = str(self.rootDir) + "\\data\\company_symbols.dat"
        self.prices_links_path = str(self.rootDir) + "\\data\\data.csv"

        self.num_threads = 50
        self.max_data = 200
        self.price_key = '"price":'
        self.iteration_count = 0

    #Check for companies file, create if necessary
    def start(self):
        #see if company file list already exists
        if not os.path.isfile(self.company_links_path):
            self.update_companies_file()
        else:
            #Set the companies list to most up-to-date file
            self.symbols = [line.rstrip('\n') for line in open(self.company_links_path, 'r')]
        self.symbol_data = [None] * len(self.symbols)

    #Write symbols to file
    def update_companies_file(self):
        #Get a list of available companies
        self.get_symbols()
        with open(self.company_links_path, "w") as file:
            for company in self.symbols:
                file.write(company + "\n")

    #Get every symbol available   
    def get_symbols(self):
        symbol_start = '<a href="/equities/'
        symbol_end = '" title'
        
        #Loop through every page on symbol list
        for i in range(1, self.symbol_lookup_end):
            page = requests.get(self.quote_url.format(i))
            soup = BeautifulSoup(page.text, 'html.parser')
            stocks = soup.findAll("tr")[1:]

            for stock in stocks:
                symbol = stock.find("a")
                symbol = str(symbol)
                symbol = symbol[len(symbol_start):symbol.find(symbol_end)]
                self.symbols.append(symbol)

    #Get the prices
    def get_prices(self, messageQ=None):
        #Save all threads to wait on join
        thread_list = []

        #Start timer and reset symbol data
        start_time = time.time()
        self.symbol_data = [None] * len(self.symbols)
        
        #Split list into even chunks and start each thread.
        for chunk in self.splitList(self.symbols, self.num_threads):
            startIndex = self.symbols.index(chunk[0])
            scrape_thread = threading.Thread(target=self.scrape_data, args=(chunk,startIndex))
            thread_list.append(scrape_thread)
            scrape_thread.start()

        #Wait for each threads with a timeout of 6 mins
        active_count = str(threading.active_count())
        for thread in thread_list:
            thread.join(360)

        #Delete any unfound quotes
        for quote in range(len(self.symbol_data) - 1, 0, -1):
            if self.symbol_data[quote] is None:
                del self.symbol_data[quote]
                
        #Now save the data
        #save_thread = threading.Thread(target=self.save_data)
        #save_thread.start()
        #Saving on a thread causes race condition for symbol_data
        self.save_data()
        self.iteration_count+=1
        
        #Check if standalone, or if messageQ. If neither (not on a thread but not main), just return time.
        if __name__ == '__main__':
            return str(round(time.time() - start_time)), active_count
            
        elif messageQ:
            messageQ.put(self.iteration_count)        
            messageQ.put(round(time.time() - start_time, 2))
        else:
            return str(round(time.time() - start_time))

    def scrape_data(self, stock_list, startIndex):
        for stock in range(len(stock_list)):
            try:
                loop_time = time.time()
                #Get the page text and extract the price
                text = urllib.request.urlopen(self.quote_url.format(stock_list[stock])).read().decode('UTF-8')
                price_index = text.find(self.price_key)
                price = text[price_index + len(self.price_key):text.find(",", price_index + len(self.price_key))]
                price = price.replace(" ", '').replace('"', '')
                
                #print("{0}: {1}, {2}".format(stock_list[stock], price, round(time.time() - loop_time, 2)))
                if self.is_number(price):
                    #print("here")
                    self.symbol_data[stock + startIndex] = [stock_list[stock], price, datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")]
                
            except urllib.error.HTTPError:
                #page doesn't exist
                continue

    def save_data(self):
        #Create file if it doesn't exist
        if not os.path.isfile(self.prices_links_path):
            open(self.prices_links_path, "w").close()
        
        with open(self.prices_links_path, "r+") as file:
            data_reader = csv.reader(file, delimiter=',')
            data_contents = [row for row in data_reader]
            
            #Step 1: See if company exists. If not, add at the end.
            #Step 2: Append data at the right spot in a row.
            #Step 3: Save data
            for symbol in range(len(self.symbol_data)):

                company = self.symbol_data[symbol][0]
                cost = self.symbol_data[symbol][1]
                time = self.symbol_data[symbol][2]

                
                #Step 1
                #See if company in data_contents, and if anything in data_contents
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
                    if empty_row < self.max_data:
                        data_contents.append(["" for column in data_contents[0]])
                
                if empty_row >= self.max_data:
                    #Move everything down a row
                    for row in range(1, len(data_contents[1:-1])+1):
                        data_contents[row][company_index] = data_contents[row+1][company_index]
                        data_contents[row][company_index+1] = data_contents[row+1][company_index+1]
                    #Set the empty row back one and make that row empty
                    empty_row -= 1
                    data_contents[empty_row][company_index] = ''
                    data_contents[empty_row][company_index+1] = ''

                #Fill the data in
                data_contents[empty_row][company_index] = str(cost)
                data_contents[empty_row][company_index+1] = str(time)
   
            #Step 3
            file.seek(0)
            for row in data_contents:
                line = ",".join(row)
                file.write(line + "\n")                    
            file.truncate()
        return
    
    """
    Helper functions section
    """
    #Split a list into n chunks
    def splitList(self, unsplitList, chunk_size):
        return [unsplitList[offs:offs+chunk_size] for offs in range(0, len(unsplitList), chunk_size)]

    #Check if float is number
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        

#If running standalone
if __name__ == '__main__':
    stonks = stonks_scraper()
    stonks.start()
    for _ in range(0, 10):
        stonks.get_prices()
    #print('done 1')
    #stonks.get_prices()

    """
    timings = []
    for i in range(10, 110, 10):
        print(i)
        num_threads = i
        stonks.num_threads = i
        time_taken, active_count = stonks.get_prices()
        timings.append([str(i), time_taken, active_count])
        timings_path = str(stonks.rootDir) + "\\data\\timings.dat"
        with open(timings_path, "w") as file:
            for row in timings:
                line = ",".join(row)
                file.write(line + "\n")   
     """
