import os
import sys
import csv
import datetime
from pathlib import Path
from stonks_sorter import stonks_sorter

class stonks_analyzer:
    def __init__(self):
        self.rootDir = Path(sys.path[0]).parent
        self.company_links_path = str(self.rootDir) + "\\data\\company_links.dat"
        self.prices_links_path = str(self.rootDir) + "\\data\\data.csv"
        self.current_stocks_path = str(self.rootDir) + "\\data\\current_stocks.csv"
        self.company_prefix = "/stocks/"
        self.company_suffix = "-stock"

        #Get pricing data
        if not os.path.isfile(self.company_links_path) or not os.path.isfile(self.prices_links_path):
            raise Exception("Need the company names file and the data file to continue.")

        #Read in data
        with open(self.prices_links_path, "r") as file:
            data_reader = csv.reader(file, delimiter=',')
            self.data_contents = [row for row in data_reader]

        #Read in stocks
        with open(self.current_stocks_path, "r") as file:
            data_reader = csv.reader(file, delimiter=',')
            self.current_stocks = [row for row in data_reader]

        #Get sorter for future price changes
        self.stonks_sorter = stonks_sorter(self.data_contents)
        self.companies = self.companies = [line.rstrip('\n') for line in open(self.company_links_path, 'r')]

        #Variables for trend/growth
        self.growth_range = 20
        self.shrink_percent = 1

    #Check each company stock prices, see if any worth buying/selling
    def check_stocks(self):
        self.sell_stocks()
        #self.buy_stocks()

    def sell_stocks(self):
        #For each stock, get the company, find the data in data_contents, see the trend, act
        for company in range(0, len(self.current_stocks[0]), 2):
            """
            for row in self.current_stocks[1:]:
                
                
                #This is for using the buy point as reference
                buyDate = row[company + 1]
                try:
                    buyDate  = datetime.datetime.strptime(row[company+1], "%m/%d/%Y %H:%M:%S").date()
                except ValueError:
                    buyDate  = datetime.datetime.strptime(row[company+1], "%m/%d/%Y %H:%M").date()
                #Get the last recorded price value
                priceInfo = self.stonks_sorter.get_price_diff(company, buyDate)
                """
            #Decide to stay or sell
            priceInfo = self.stonks_sorter.get_price_diff(company, index=self.growth_range)
            
#Structure: 
#Current amount, decide what to do.
#If have enough, and stocks have been growing, buy.
#If stocks are dipping (>-1%?), sell.
#Woken up after every cycle on scraper to make decisions.
#Save current stock info in .CSV?
#Save info as 2D list, [company, stock]

#How to decide if company growing?
#Step 1, see if any change since last?
#Unecessary, only called after scraper update.
#See if trend up or down... starting point? Beginning of day, last 3 points...
#Do last 10 points, see trend.
#OR
#Can't do buy price - will only sell when at a loss.
#Check growth since buy price. If growth < 0 n times consecutively or losing > 1%, sell
if __name__ == '__main__':
    analyzer = stonks_analyzer()
    analyzer.check_stocks()
