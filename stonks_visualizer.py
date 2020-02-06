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
        timestamps = dates.date2num([datetime.datetime.strptime(entry[1], "%Y-%m-%d %H:%M:%S.%f") for entry in pricing_data if entry[1]])

        plt.plot_date(timestamps, prices, '-o')
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
        
        self.greatestIncreaseRange = IntVar()
        #Create radios for highest increase
        self.greatestIncreaseDayRadio = Radiobutton(self.moreInfoFrame, text="Day", variable=self.greatestIncreaseRange, value=0, command=self.greatest_increase)
        self.greatestIncreaseDayRadio.grid(row=0, column=0, sticky=N)
        self.greatestIncreaseWeekRadio = Radiobutton(self.moreInfoFrame, text="Week", variable=self.greatestIncreaseRange, value=1, command=self.greatest_increase)
        self.greatestIncreaseWeekRadio.grid(row=0, column=1, sticky=N)
        self.greatestIncreaseMonthRadio = Radiobutton(self.moreInfoFrame, text="1 Month", variable=self.greatestIncreaseRange, value=2, command=self.greatest_increase)
        self.greatestIncreaseMonthRadio.grid(row=0, column=2, sticky=N)
        self.greatestIncrease6MonthRadio = Radiobutton(self.moreInfoFrame, text="6 Months", variable=self.greatestIncreaseRange, value=3, command=self.greatest_increase)
        self.greatestIncrease6MonthRadio.grid(row=0, column=3, sticky=N)
        self.greatestIncreaseYearRadio = Radiobutton(self.moreInfoFrame, text="Year", variable=self.greatestIncreaseRange, value=4, command=self.greatest_increase)
        self.greatestIncreaseYearRadio.grid(row=0, column=4, sticky=N)
        
        self.greatestIncreaseLabel = Label(self.moreInfoFrame, text="hi", borderwidth=2, relief="groove")
        #self.greatestIncreaseLabel.grid(row=0, column=1, sticky=E)
        self.greatest_increase()
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
        earliestDate = ""
        if self.greatestIncreaseRange.get() == 0: #day
            earliestDate = datetime.datetime.today().date()
        elif self.greatestIncreaseRange.get() == 1: #week
            earliestDate = (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        elif self.greatestIncreaseRange.get() == 2: #month
            today = datetime.datetime.today().date()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth == 1:
                earliestDate = datetime.datetime.today().date().replace(month=12,year=currentYear-1)
            else:
                earliestDate = datetime.datetime.today().date().replace(month=currentMonth-1)
        elif self.greatestIncreaseRange.get() == 3: #6 months
            today = datetime.datetime.today()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth <= 6:
                earliestDate = datetime.datetime.today().date().replace(month=12+(currentMonth-6),year=currentYear-1)
            else:
                earliestDate = datetime.datetime.today().date().replace(month=currentMonth-6)
        elif self.greatestIncreaseRange.get() == 4: #year
            currentYear = datetime.datetime.today().year
            earliestDate = datetime.datetime.today().date().replace(year=currentYear-1)
        
        #timestamps = dates.date2num([datetime.strptime(entry[1], "%Y-%m-%d %H:%M:%S.%f") for entry in pricing_data if entry[1]])
            
visualizer = stonks_visualizer()
visualizer.gui_initialize()
