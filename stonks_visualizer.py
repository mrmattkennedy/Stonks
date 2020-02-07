import os
import sys
import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from tkinter import *

class stonks_visualizer():
    def __init__(self):
        #Initialize vars
        self.company_links_path = sys.path[0] + "\\data\\company_links.dat"
        self.prices_links_path = sys.path[0] + "\\data\\data.csv"
        self.company_prefix = "/stocks/"
        self.company_suffix = "-stock"
        self.selected_company = None

        #Get pricing data
        if not os.path.isfile(self.company_links_path) or not os.path.isfile(self.prices_links_path):
            raise Exception("Need the company names file and the data file to continue.")
        
        with open(self.prices_links_path, "r") as file:
            data_reader = csv.reader(file, delimiter=',')
            self.data_contents = [row for row in data_reader]
        
        #Initialize GUI
        self.gui = Tk()
        self.gui.title('Stonks')

        #Mainframe for all widgets
        self.mainframe = Frame(self.gui)
        self.mainframe.grid(column=0,row=0, sticky=(N,W,E,S))
        self.mainframe.pack(pady = 5, padx = 10)

        #Popup menu to select a stock
        self.tkvar = StringVar(self.mainframe)
        self.tkvar.trace('w', self.change_dropdown)
        self.choices = [line[len(self.company_prefix):len(line)-len(self.company_suffix) - 1] for line in open(self.company_links_path, "r").readlines()]
        self.popupMenu = OptionMenu(self.mainframe, self.tkvar, *self.choices)
        self.popupMenu.grid(row=0, column=1, sticky=E)

        #Label and entry to go with popup menu
        self.popupLabel = Label(self.mainframe, text="Choose a company")
        self.popupLabel.grid(row=0, column=0, sticky=W)
        self.companyEntry = Entry(self.mainframe, text="Enter a company")
        self.companyEntry.grid(row=1, column=0, columnspan=2, sticky=(W,E,S))

        #Button to visualize
        self.displayStocks = Button(self.mainframe, text="Show stock", command=self.displayStockInfo)
        self.displayStocks.grid(row=2, column=0, columnspan=1, pady=3, sticky=(W,S))
        self.displayMultiple = Button(self.mainframe, text="More info", command=self.more_info)
        self.displayMultiple.grid(row=2, column=1, columnspan=1, pady=3, sticky=(E,S))
        
    def gui_initialize(self):
        self.gui.mainloop()

    def change_dropdown(self, *args):
        self.companyEntry.delete(0, END)
        self.companyEntry.insert(0, self.tkvar.get())
        
    def displayStockInfo(self):
        self.selected_company = self.companyEntry.get()
        #Step 1: Find company.
        if len(self.data_contents) > 0:
            if self.selected_company not in self.data_contents[0]:
                self.companyEntry.delete(0, END)
                self.companyEntry.insert(0, "Company not in spreadsheet.")
        else:
            self.companyEntry.delete(0, END)
            self.companyEntry.insert(0, "Company not in spreadsheet.")


        #Step 2: Get index of company.
        company_index = self.data_contents[0].index(self.selected_company)

        #Step 3: Get all rows in that column, append to 2D list.
        pricing_data = []
        try:
            for row in self.data_contents[1:]: #loop through each row except first
                pricing_data.append([row[company_index], row[company_index+1]])
        except IndexError:
            pass

        #Step 4: Visualize
        #Need if entry[i] on end for potential blank values
        prices = [float(entry[0]) for entry in pricing_data if entry[0]]
        #Convert from saved string to list of datetime.datetime objects for matplotlib
        timestamps = dates.date2num([datetime.datetime.strptime(entry[1], "%m/%d/%Y %H:%M:%S") for entry in pricing_data if entry[1]])

        priceDiff = max(prices) - min(prices)
        minPrice = min(prices)
        maxPrice = max(prices)
        minLabel = minPrice + (priceDiff * 0.2)
        maxLabel = maxPrice + (priceDiff * 0.2)
  
        plt.figure(figsize=(9.6,7.2)).canvas.set_window_title(self.selected_company)
        plt.plot_date(timestamps, prices, '-o', markersize=4)
        if priceDiff != 0:
            plt.ylim((minPrice,maxLabel))
        plt.fill_between(timestamps, prices, color='blue', alpha=0.1)
        plt.grid()
        plt.show()

    """
    Info displayed here:
    1. Highest risers since (today, week, month, 6 months, 12 months)
    2.
    """
    def more_info(self):
        #Create secondary GUI and frame
        self.moreInfoGUI = Toplevel(self.gui)
        self.moreInfoFrame = Frame(self.moreInfoGUI, borderwidth = 2)
        self.moreInfoFrame.grid(column=0,row=0, sticky=(N,W,E,S))
        self.moreInfoFrame.pack(pady = 5, padx = 10)

        #Create options menu
        self.rangeChoices = ["Day", "Week", "1 Month", "6 Months", "Year"]
        self.greatestIncreaseRange = StringVar()
        self.rangeMenu = OptionMenu(self.moreInfoFrame, self.greatestIncreaseRange, *self.rangeChoices)
        self.rangeMenu.grid(row=1, column=0, sticky=(N,W,E))

        #Create button and input for range and number of companies
        self.numberCompanies = IntVar()
        self.greatestIncreaseNumCompanies = Entry(self.moreInfoFrame)
        self.greatestIncreaseNumCompanies.insert(0, "Number of companies")
        self.greatestIncreaseNumCompanies.grid(row=0, column=0, columnspan=2, sticky=W)
        self.greatestIncreaseButton = Button(self.moreInfoFrame, text="Search", command=self.greatest_increase)
        self.greatestIncreaseButton.grid(row=1, column=1, columnspan=1, sticky=E)
        
    """
    Helper function
    Get the 5 highest risers in a given frequency
    
    Loop through each company, find the farthest acceptable date for range
    Calculate difference from that entry to most current entry
    Get top 5
    """
    def greatest_increase(self):
        #Need data to process
        if not len(self.data_contents) > 0:
            return
        
        #Get range for dates
        self.earliestDate = self.get_earliest_date()
        
        #Go through every company, and get every value until the day is no longer in range
        self.numberCompanies = int(self.greatestIncreaseNumCompanies.get())
        increaseList = self.get_increase_list(self.numberCompanies)
        
        #Display table headers
        tempName = Label(self.moreInfoFrame, text="Company", borderwidth=4, relief="ridge")
        tempName.grid(row=2, column=0, sticky=(N,S,E,W))
        tempStart = Label(self.moreInfoFrame, text="Start", borderwidth=4, relief="ridge")
        tempStart.grid(row=2, column=1, sticky=(N,S,E,W))
        tempEnd = Label(self.moreInfoFrame, text="End", borderwidth=4, relief="ridge")
        tempEnd.grid(row=2, column=2, sticky=(N,S,E,W))
        tempDiff = Label(self.moreInfoFrame, text="Diff", borderwidth=4, relief="ridge")
        tempDiff.grid(row=2, column=3, sticky=(N,S,E,W))

        #Display info
        for company in range(len(increaseList)):
            tempName = Label(self.moreInfoFrame, text=increaseList[company][0], borderwidth=2, relief="groove")
            tempName.grid(row=company + 3, column=0, sticky=(N,S,E,W))
            tempStart = Label(self.moreInfoFrame, text=increaseList[company][2], borderwidth=2, relief="groove")
            tempStart.grid(row=company + 3, column=1, sticky=(N,S,E,W))
            tempEnd = Label(self.moreInfoFrame, text=increaseList[company][3], borderwidth=2, relief="groove")
            tempEnd.grid(row=company + 3, column=2, sticky=(N,S,E,W))
            tempDiff = Label(self.moreInfoFrame, text=increaseList[company][1], borderwidth=2, relief="groove")
            tempDiff.grid(row=company + 3, column=3, sticky=(N,S,E,W))
    """
    Helper function
    Get the earliest date for the highest increase range
    """
    def get_earliest_date(self):
        if self.greatestIncreaseRange.get() == "Day": #day
            return datetime.datetime.today().date()
        elif self.greatestIncreaseRange.get() == "Week": #week
            return (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        elif self.greatestIncreaseRange.get() == "1 Month": #month
            today = datetime.datetime.today().date()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth == 1:
                return datetime.datetime.today().date().replace(month=12,year=currentYear-1)
            else:
                return datetime.datetime.today().date().replace(month=currentMonth-1)
        elif self.greatestIncreaseRange.get() == "6 Months": #6 months
            today = datetime.datetime.today()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth <= 7:
                return datetime.datetime.today().date().replace(month=12+(currentMonth-6),year=currentYear-1)
            else:
                return datetime.datetime.today().date().replace(month=currentMonth-6)
        elif self.greatestIncreaseRange.get() == "Year": #year
            currentYear = datetime.datetime.today().year
            return datetime.datetime.today().date().replace(year=currentYear-1)

        return ""

    """
    Helper function
    Get list of greatest increases of stocks in data
    """
    def get_increase_list(self, length):
        retList = []
        for company in range(0, len(self.data_contents[0]), 2):
            
            #Get the last recorded price value
            last_row = len(self.data_contents) - 1
            empty_row = True
            
            while empty_row:
                if not self.data_contents[last_row][company]:
                    last_row-=1
                    continue
                empty_row = False

            #Get the prices starting at the last recorded price value
            acceptable_range = True
            starting_price = -1
            current_row = last_row
            ending_price = self.data_contents[last_row][company]
            
            while acceptable_range:
                pastDate = datetime.datetime.strptime(self.data_contents[current_row][company+1], "%m/%d/%Y %H:%M:%S").date()
                if pastDate >= self.earliestDate and current_row != 1:
                    starting_price = self.data_contents[current_row][company]
                    current_row-=1
                else:
                    acceptable_range = False

            #Get the price difference and append it
            increase = round(float(ending_price) - float(starting_price), 2)
            retList.append([self.data_contents[0][company], increase, round(float(starting_price), 2), round(float(ending_price), 2)])

        #Sort list according to greatest increase
        retList = sorted(retList, key = lambda x: x[1])
        return retList[-length:]

        
visualizer = stonks_visualizer()
visualizer.gui_initialize()
