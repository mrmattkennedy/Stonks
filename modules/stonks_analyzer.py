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
        self.cash_path = str(self.rootDir) + "\\data\\cash.dat"
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
        self.companies = [line.rstrip('\n') for line in open(self.company_links_path, 'r')]
        self.cash = float([line.rstrip('\n') for line in open(self.cash_path, 'r')][0])
        
        #Variables for trend/growth
        self.growth_range = 20
        self.shrink_percent = 0
        self.growth_percent = 0.2
        self.growth_amount = 0.5

    #Check each company stock prices, see if any worth buying/selling
    def check_stocks(self, messageQ=None):
        self.sell_stocks(messageQ)
        self.buy_stocks(messageQ)
        
        with open(self.current_stocks_path, "r+") as file:
            file.seek(0)
            for row in self.current_stocks:
                line = ",".join(row)
                file.write(line + "\n")                    
            file.truncate()

        with open(self.cash_path, "r+") as file:
            file.seek(0)
            file.write(str(self.cash))                    
            file.truncate()
            
    def sell_stocks(self, messageQ):
        #For each stock, get the company, find the data in data_contents, see the trend, act
        if len(self.current_stocks) == 0:
            return
        cashMade = 0
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
            company_index = self.data_contents[0].index(self.current_stocks[0][company])
            priceInfo = self.stonks_sorter.get_price_diff(company_index, index=self.growth_range)
            if priceInfo[3] < self.shrink_percent:
                for stock in range(1, len(self.current_stocks)):
                    if len(self.current_stocks[stock]) <= company:
                        break
                    #Get last row for that one
                    moneyMade = self.get_last_price(company) - float(self.current_stocks[stock][company])
                    self.cash += moneyMade
                    cashMade+= moneyMade
                    self.current_stocks[stock][company] = ''
                    self.current_stocks[stock][company+1] = ''

        if messageQ:
            messageQ.put(cashMade)
    def buy_stocks(self, messageQ):
        #Get increase over last range, buy if increasing
        cashSpent = 0
        for company in range(0, len(self.data_contents[0]), 2):
            priceInfo = self.stonks_sorter.get_price_diff(company, index=self.growth_range)
            if priceInfo[3] > self.growth_percent or priceInfo[2] > self.growth_amount:
                price = self.get_last_price(company)
                if self.cash < price:
                    continue
                
                self.cash -= price
                cashSpent += price
                last_row = self.get_last_row(company)
                if last_row == -2:
                    self.current_stocks.append([self.data_contents[0][company]])
                    self.current_stocks[0].append('')
                    self.current_stocks.append([str(price), datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")])
                elif last_row == -1:
                    self.current_stocks[0].append(self.data_contents[0][company])
                    self.current_stocks[0].append('')
                    self.current_stocks[last_row].append(str(price))
                    self.current_stocks[last_row].append(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
                else:
                    self.current_stocks[last_row][company] = str(price)
                    self.current_stocks[last_row][company+1] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if messageQ:
            messageQ.put(cashSpent)

        
    def get_last_price(self, company):
        #Get the last recorded price value
        last_row = len(self.data_contents) - 1
        empty_row = True
        
        while empty_row:
            if not self.data_contents[last_row][company]:
                last_row-=1
                continue
            empty_row = False

        #Get the prices starting at the last recorded price value
        return float(self.data_contents[last_row][company])

    def get_last_row(self, company):
        if len(self.current_stocks) == 0:
            return -2
        #Get the last recorded price value
        if not company in self.current_stocks[0]:
            return -1
        last_row = len(self.current_stocks) - 1
        empty_row = True
        
        while empty_row:
            if not self.data_contents[last_row][company]:
                last_row-=1
                continue
            empty_row = False

        #Get the prices starting at the last recorded price value
        return last_row

    
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
