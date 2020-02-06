import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from tkinter import *
from datetime import datetime

class stonks_visualizer():
    def __init__(self):
        #Initialize vars
        self.company_links_path = sys.path[0] + "\\data\\company_links.dat"
        self.prices_links_path = sys.path[0] + "\\data\\data.csv"
        self.company_prefix = "/stocks/"
        self.company_suffix = "-stock"
        self.selected_company = None

        #Get pricing data
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
        self.popupMenu.grid(row=0, column=1, sticky=W)

        #Label and entry to go with popup menu
        self.popupLabel = Label(self.mainframe, text="Choose a company")
        self.popupLabel.grid(row=0, column=0, sticky=W)
        self.companyEntry = Entry(self.mainframe, text="Enter a company")
        self.companyEntry.grid(row=1, column=0, columnspan=2, sticky=(W,E,S))

        #Button to visualize
        self.displayStocks = Button(self.mainframe, text="Show info", command=self.displayStockInfo)
        self.displayStocks.grid(row=2, column=0, columnspan=2, pady=3, sticky=(W,E,S))
        
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
        prices = [float(entry[0]) for entry in pricing_data if entry[0]]
        #Convert from saved string to list of datetime.datetime objects for matplotlib
        timestamps = dates.date2num([datetime.strptime(entry[1], "%Y-%m-%d %H:%M:%S.%f") for entry in pricing_data if entry[1]])

        plt.plot_date(timestamps, prices, '-o')
        plt.show()
        
visualizer = stonks_visualizer()
visualizer.gui_initialize()
