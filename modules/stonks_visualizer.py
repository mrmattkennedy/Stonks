import os
import sys
import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from tkinter import *
from pathlib import Path
from stonks_sorter import stonks_sorter

class stonks_visualizer():
    def __init__(self):
        #Initialize vars
        self.rootDir = Path(sys.path[0]).parent
        self.company_links_path = str(self.rootDir) + "\\data\\company_symbols.dat"
        self.prices_links_path = str(self.rootDir) + "\\data\\data.csv"
        self.company_prefix = "/stocks/"
        self.company_suffix = "-stock"
        self.selected_company = None

        #Get pricing data
        if not os.path.isfile(self.company_links_path) or not os.path.isfile(self.prices_links_path):
            raise Exception("Need the company names file and the data file to continue.")
        
        with open(self.prices_links_path, "r") as file:
            data_reader = csv.reader(file, delimiter=',')
            self.data_contents = [row for row in data_reader]

        #For sorting and other information
        self.stonks_sorter = stonks_sorter(self.data_contents)
        
        #Initialize GUI
        self.gui = Tk()
        self.gui.title('Stonks Visualizer')

        #Mainframe for all widgets
        self.mainframe = Frame(self.gui)
        self.mainframe.grid(column=0,row=0, sticky=(N,W,E,S))
        self.mainframe.pack(pady = 5, padx = 10)

        #Popup menu to select a stock
        self.tkvar = StringVar(self.mainframe)
        self.tkvar.trace('w', self.change_dropdown)
        self.choices = [line.strip() for line in open(self.company_links_path, "r").readlines()]
        self.popupMenu = OptionMenu(self.mainframe, self.tkvar, *self.choices)
        self.popupMenu.grid(row=0, column=1, sticky=E)

        #Label and entry to go with popup menu
        self.popupLabel = Label(self.mainframe, text="Choose a company")
        self.popupLabel.grid(row=0, column=0, sticky=W)
        self.companyEntry = Entry(self.mainframe)
        self.companyEntry.grid(row=1, column=0, columnspan=2, sticky=(W,E,S))

        #Button to visualize
        self.displayStocks = Button(self.mainframe, text="Show stock", command=self.displayStockInfo)
        self.displayStocks.grid(row=2, column=0, columnspan=1, pady=3, sticky=(W,S))
        self.displayMultiple = Button(self.mainframe, text="More info", command=self.more_info)
        self.displayMultiple.grid(row=2, column=1, columnspan=1, pady=3, sticky=(E,S))

        #Date range
        self.greatestIncreaseRange = StringVar()
        self.graphRangeChoices = ["Day", "Week", "1 Month", "6 Months", "Year"]
        self.graphRangeMenu = OptionMenu(self.mainframe, self.greatestIncreaseRange, *self.graphRangeChoices)
        self.graphRangeMenu.grid(row=3, column=0, columnspan=2, sticky=(S,E,W))
        
    def gui_initialize(self):
        self.gui.mainloop()

    def change_dropdown(self, *args):
        self.companyEntry.delete(0, END)
        self.companyEntry.insert(0, self.tkvar.get())
        
    def displayStockInfo(self):
        self.selected_company = self.companyEntry.get()
        if not self.selected_company:
            return
        
        #Step 1: Find company.
        if len(self.data_contents) > 0:
            if self.selected_company not in self.data_contents[0]:
                self.companyEntry.delete(0, END)
                self.companyEntry.insert(0, "Company not in spreadsheet.")
                return
        else:
            self.companyEntry.delete(0, END)
            self.companyEntry.insert(0, "Company not in spreadsheet.")
            return

        #Step 2: Get index of company.
        company_index = self.data_contents[0].index(self.selected_company)
        
        #Step 3: Get all rows in that column, append to 2D list.
        pricing_data = []
        try:
            #If earliest date is a think, then compare. If not, grab them all.
            if self.greatestIncreaseRange.get():
                self.earliestDate = self.stonks_sorter.get_earliest_date(self.greatestIncreaseRange.get())
                
                for row in self.data_contents[1:]: #loop through each row except first
                    pastDate = datetime.datetime.strptime(row[company_index+1], "%m/%d/%Y %H:%M:%S").date()
                    if pastDate >= self.earliestDate:
                        pricing_data.append([row[company_index], row[company_index+1]])
            else:
                for row in self.data_contents[1:]: #loop through each row except first
                    pricing_data.append([row[company_index], row[company_index+1]])
                    
        except IndexError:
            pass
        except ValueError:
            pass

        #Step 4: Visualize
        #Need if entry[i] on end for potential blank values
        prices = [float(entry[0]) for entry in pricing_data if entry[0]]
        #Convert from saved string to list of datetime.datetime objects for matplotlib
        #print(pricing_data[1][1].seconds)
        
        timestamps = []
        #Need this; when importing datetime strings, if seconds are 00, they get removed.
        for entry in pricing_data:
            try:
                if entry[1]:
                    timestamps.append(dates.date2num(datetime.datetime.strptime(entry[1], "%m/%d/%Y %H:%M:%S")))
            except ValueError:
                timestamps.append(dates.date2num(datetime.datetime.strptime(entry[1], "%m/%d/%Y %H:%M")))
            
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
        self.increaseList = []
        self.tableElems = []
        self.tableRow = 3
        
        #Create secondary GUI and frame
        self.moreInfoGUI = Toplevel(self.gui)
        self.moreInfoFrame = Frame(self.moreInfoGUI, borderwidth = 2)
        self.moreInfoFrame.grid(column=0,row=0, sticky=(N,W,E,S))
        self.moreInfoFrame.pack(pady = 5, padx = 10)

        #Create options menu
        self.rangeChoices = ["Day", "Week", "1 Month", "6 Months", "Year"]
        self.greatestIncreaseRange = StringVar()
        self.rangeMenu = OptionMenu(self.moreInfoFrame, self.greatestIncreaseRange, *self.rangeChoices)
        self.rangeMenu.grid(row=1, column=0, sticky=(N,W))

        #Create options menu
        self.growthChoices = ["$", "%"]
        self.growthVar = StringVar()
        self.growthChoicesMenu = OptionMenu(self.moreInfoFrame, self.growthVar, *self.growthChoices)
        self.growthChoicesMenu.grid(row=1, column=1, sticky=(N))

        #Create options menu
        self.growthDirectionChoices = ["Increase", "Decrease"]
        self.growthDirectionVar = StringVar()
        self.growthDirectionMenu = OptionMenu(self.moreInfoFrame, self.growthDirectionVar, *self.growthDirectionChoices)
        self.growthDirectionMenu.grid(row=1, column=2, sticky=(N,E))

        #Create button and input for range and number of companies
        self.numberCompanies = IntVar()
        self.greatestIncreaseNumCompanies = Entry(self.moreInfoFrame)
        self.greatestIncreaseNumCompanies.insert(0, "Number of companies")
        self.greatestIncreaseNumCompanies.grid(row=0, column=0, columnspan=3, sticky=(N,W,E))
        self.greatestIncreaseButton = Button(self.moreInfoFrame, text="Search", command=self.greatest_increase)
        self.greatestIncreaseButton.grid(row=2, column=0, columnspan=3, sticky=(S,W,E))
        
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

        #If the list exists and no settings have changed, don't go through all the data again
        if not self.increaseList:
            #Get range for dates
            self.earliestDate = self.stonks_sorter.get_earliest_date(self.greatestIncreaseRange.get())
            
            #Go through every company, and get every value until the day is no longer in range
            self.numberCompanies = int(self.greatestIncreaseNumCompanies.get())
            self.increaseList = self.stonks_sorter.get_increase_list(
                self.numberCompanies,
                self.earliestDate,
                self.growthDirectionVar.get(),
                self.growthVar.get())

            #Save current choices to determine if change was made
            self.currentGrowth = self.growthVar.get()
            self.currentGrowthDirection = self.growthDirectionVar.get()
            
        else:
            #See if earliest date changed
            currentEarliestDate = self.earliestDate
            self.earliestDate = self.stonks_sorter.get_earliest_date(self.greatestIncreaseRange.get())
            changedRange = False if currentEarliestDate == self.earliestDate else True

            #See if # companies changed
            currentNumberCompanies = self.numberCompanies
            self.numberCompanies = int(self.greatestIncreaseNumCompanies.get())
            changedNumber = False if currentNumberCompanies == self.numberCompanies else True

            #See if growth var changed
            changedGrowthVar = False if self.growthVar.get() == self.currentGrowth else True

            #See if growth direction changed
            changedGrowthDirection = False if self.growthDirectionVar.get() == self.currentGrowthDirection else True

            #Set current choices
            self.currentGrowth = self.growthVar.get()
            self.currentGrowthDirection = self.growthDirectionVar.get()

            #print(changedRange, changedNumber, changedGrowthVar, changedGrowthDirection)
            if changedRange or changedNumber or changedGrowthVar or changedGrowthDirection:
                self.increaseList = self.stonks_sorter.get_increase_list(
                    self.numberCompanies,
                    self.earliestDate,
                    self.growthDirectionVar.get(),
                    self.growthVar.get())
        #Remove all prior elements and clear list
        for element in self.tableElems:
            element.destroy()
        self.tableElems.clear()
        
        #Display table headers
        tempName = Label(self.moreInfoFrame, text="Company", borderwidth=4, relief="ridge")
        tempName.grid(row=self.tableRow, column=0, sticky=(N,S,E,W))
        tempStart = Label(self.moreInfoFrame, text="Start", borderwidth=4, relief="ridge")
        tempStart.grid(row=self.tableRow, column=1, sticky=(N,S,E,W))
        tempEnd = Label(self.moreInfoFrame, text="End", borderwidth=4, relief="ridge")
        tempEnd.grid(row=self.tableRow, column=2, sticky=(N,S,E,W))
        tempDiff = Label(self.moreInfoFrame, text="Diff", borderwidth=4, relief="ridge")
        tempDiff.grid(row=self.tableRow, column=3, sticky=(N,S,E,W))
        tempDiffPercent = Label(self.moreInfoFrame, text="% Diff", borderwidth=4, relief="ridge")
        tempDiffPercent.grid(row=self.tableRow, column=4, sticky=(N,S,E,W))

        #Display info
        for company in range(len(self.increaseList)):
            tempName = Label(self.moreInfoFrame, text=self.increaseList[company][0], borderwidth=2, relief="groove")
            tempName.grid(row=company + self.tableRow + 1, column=0, sticky=(N,S,E,W))
            tempStart = Label(self.moreInfoFrame, text=self.increaseList[company][3], borderwidth=2, relief="groove")
            tempStart.grid(row=company + self.tableRow + 1, column=1, sticky=(N,S,E,W))
            tempEnd = Label(self.moreInfoFrame, text=self.increaseList[company][4], borderwidth=2, relief="groove")
            tempEnd.grid(row=company + self.tableRow + 1, column=2, sticky=(N,S,E,W))
            tempDiff = Label(self.moreInfoFrame, text="$" + str(self.increaseList[company][1]), borderwidth=2, relief="groove")
            tempDiff.grid(row=company + self.tableRow + 1, column=3, sticky=(N,S,E,W))
            tempDiffPercent = Label(self.moreInfoFrame, text=str(self.increaseList[company][2]) + "%", borderwidth=2, relief="groove")
            tempDiffPercent.grid(row=company + self.tableRow + 1, column=4, sticky=(N,S,E,W))
            self.tableElems.append(tempName)
            self.tableElems.append(tempStart)
            self.tableElems.append(tempEnd)
            self.tableElems.append(tempDiff)
            self.tableElems.append(tempDiffPercent)

if __name__ == '__main__':
    visualizer = stonks_visualizer()
    visualizer.gui_initialize()
