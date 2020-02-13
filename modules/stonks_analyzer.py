import os
import sys
import csv
import pdb
import datetime
import traceback
from pathlib import Path
from multiprocessing import Queue
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
        self.shrink_range = 1 #Go 1 back
        self.shrink_percent = 0
        self.growth_range = 1 
        self.growth_percent = 0.2
        self.growth_amount = 1

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
        
        #If threading, messageQ will hold something. If not called on thread, just return value.
        total_value = self.get_total_value(messageQ)
        if total_value:
            return total_value

    """
    Algorithm for selling:
    Loop through each company in current stocks file.
    Get the index of the company, get the price info on the company for the last 2
    Check the # of times decreasing: if 3, then sell.
    If decreasing but hasn't happened 3 times, increment.
    If increasing, decrement count by 1 until 0.
    """
    def sell_stocks(self, messageQ):
        #If there are no current stocks, just return.
        if len(self.current_stocks) == 0:
            return
        
        #For each stock, get the company, find the data in data_contents, see the trend, act
        for company in range(0, len(self.current_stocks[0]), 2):            
            company_index = self.data_contents[0].index(self.current_stocks[0][company])
            priceInfo = self.stonks_sorter.get_price_diff(company_index, index=self.shrink_range)

            #Loop through each row with row var as stock
            for stock in range(1, len(self.current_stocks)):
                #Check if there are any stocks in the row for the company. If not, break
                if len(self.current_stocks[stock]) <= company:
                    break
                #See if shrinked
                if priceInfo[3] < self.shrink_percent:
                    #See how many times var has shrinked
                    shrinkCount = self.current_stocks[stock][company+1]
                    if shrinkCount:
                        shrinkCount = int(shrinkCount)

                        #If it's less than 3, increment. If 3, sell.
                        if shrinkCount < 3:
                            shrinkCount+=1
                            self.current_stocks[stock][company+1] = str(shrinkCount)
                        else:
                            company_index = self.data_contents[0].index(self.current_stocks[0][company])
                            self.cash += self.get_last_price(company_index)
                            print("Sold " + self.current_stocks[0][company] + " for " + str(moneyMade))
                            self.current_stocks[stock][company] = ''
                            self.current_stocks[stock][company+1] = ''

    
    def buy_stocks(self, messageQ):
        #Get increase list
        self.increase_list = self.stonks_sorter.get_increase_list(
                                        500,
                                        self.stonks_sorter.get_earliest_date("Day"),
                                        "Increase",
                                        "$")
        for company in range(len(self.increase_list)-1, 0, -1):
            #Growth is too minimal to invest
            if self.increase_list[company][2] < self.growth_percent and self.increase_list[company][1] < self.growth_amount:
                return
            
            data_contents_index = self.data_contents[0].index(self.increase_list[company][0])
            price = self.get_last_price(data_contents_index)
            
            if self.cash < price:
                continue
            
            self.cash -= price
            company_index = -1
            if len(self.current_stocks) != 0:
                try:
                    company_index = self.current_stocks[0].index(self.increase_list[company][0])
                except ValueError:
                    pass #means company not in list, index still -1
                
            first_row = self.get_first_row(company_index)

            if first_row == -2: #No current stocks at all
                self.current_stocks.append([self.increase_list[company][0]])
                self.current_stocks[0].append('')
                self.current_stocks.append([str(price), "0"])
            elif first_row == -1: #Company not in the stock spreadsheet
                self.current_stocks[0].append(self.increase_list[company][0])
                self.current_stocks[0].append('')
                self.current_stocks[first_row].append(str(price))
                self.current_stocks[first_row].append("0")
            else:
                if first_row == len(self.current_stocks):
                    print(self.current_stocks, company_index)
                    self.current_stocks.append(['']*len(self.current_stocks[0]))
                    self.current_stocks[first_row][company_index] = str(price)
                    self.current_stocks[first_row][company_index+1] = "0"
                else:
                    self.current_stocks[first_row][company_index] = str(price)
                    self.current_stocks[first_row][company_index+1] = "0"


    def get_total_value(self, messageQ):
        total_value = self.cash
        for row in self.current_stocks[1:]:
            for value in row[::2]:
                if value:
                    total_value += float(value)
        
        if not messageQ:
            return total_value
        else:
            messageQ.put(total_value)
            
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

    #Get first open row
    def get_first_row(self, company_index):
        try:
            if len(self.current_stocks) == 0:
                return -2

            #company not in list
            if company_index == -1:
                return -1

            first_row = 1
            filled_row = True

        
            #Work forwards starting at column
            while filled_row:
                if first_row == len(self.current_stocks):
                    break
                elif self.current_stocks[first_row][company_index]:
                    first_row+=1
                    continue
                
                filled_row = False
                
            #Get the prices starting at the last recorded price value
            return first_row
        except:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
    
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
