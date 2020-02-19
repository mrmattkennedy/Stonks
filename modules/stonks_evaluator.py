import os
import csv
import sys
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from tkinter import *
from pathlib import Path


class stonks_evaluator:
    def __init__(self):
        #Get file to open
        self.rootDir = Path(sys.path[0]).parent
        self.value_over_time_path = str(self.rootDir) + "\\data\\value_over_time.csv"

        #Read in values
        with open(self.value_over_time_path, "r+") as file:
            data_reader = csv.reader(file, delimiter=',')
            self.values_over_time = [row for row in data_reader]
            
        #Initialize GUI
        self.table_widgets = []
        self.gui = Tk()
        self.gui.title('Evaluator')

        #Mainframe for all widgets
        self.mainFrame = Frame(self.gui)
        self.mainFrame.grid(column=0, row=0, sticky=(N,W,E,S))
        self.mainFrame.pack(pady = 5, padx = 10)

        #Buttons
        self.tableBtn = Button(self.mainFrame, text="Table", command=self.create_table, height=2, width=8)
        self.tableBtn.grid(row=0, column=0, sticky=(N,S,W), padx=5)
        self.graphBtn = Button(self.mainFrame, text="Graph", command=self.create_graph, height=2, width=8)
        self.graphBtn.grid(row=0, column=1, sticky=(N,S,E), padx=5)

        self.table_showing = False
        self.tableRow = 3
        self.gui.mainloop()

    def create_graph(self):
        
        values = [round(float(entry[1]), 2) for entry in self.values_over_time]
        priceDiff = max(values) - min(values)
        timestamps = []
        for entry in self.values_over_time:
            try:
                if entry[1]:
                    timestamps.append(dates.date2num(datetime.datetime.strptime(entry[3], "%m/%d/%Y %H:%M:%S")))
            except ValueError:
                timestamps.append(dates.date2num(datetime.datetime.strptime(entry[3], "%m/%d/%Y %H:%M")))

        minPrice = min(values)
        maxPrice = max(values)
        minLabel = minPrice + (priceDiff * 0.2)
        maxLabel = maxPrice + (priceDiff * 0.2)
        plt.figure(figsize=(9.6,7.2)).canvas.set_window_title("Value over time")
        plt.plot_date(timestamps, values, '-o', markersize=4)
        if priceDiff != 0:
            plt.ylim((minPrice,maxLabel))
        plt.fill_between(timestamps, values, color='blue', alpha=0.1)
        plt.grid()
        plt.show()

        
    def show_table(self):
        if self.table_showing:
            #Remove all prior elements and clear list
            for widget in self.table_widgets:
                widget.destroy()
            self.table_widgets.clear()
            self.table_showing = False
        else:
            self.table_showing = True
            self.create_table()

            
    def create_table(self):
        #Display table headers
        tempTotal = Label(self.mainFrame, text="Total", borderwidth=4, relief="ridge")
        tempTotal.grid(row=self.tableRow, column=0, sticky=(N,S,E,W))
        tempActual = Label(self.mainFrame, text="Actual", borderwidth=4, relief="ridge")
        tempActual.grid(row=self.tableRow, column=1, sticky=(N,S,E,W))
        tempDiff = Label(self.mainFrame, text="Diff", borderwidth=4, relief="ridge")
        tempDiff.grid(row=self.tableRow, column=2, sticky=(N,S,E,W))
        tempChange = Label(self.mainFrame, text="Change", borderwidth=4, relief="ridge")
        tempChange.grid(row=self.tableRow, column=3, sticky=(N,S,E,W))

        #Append headers to list to delete later
        self.table_widgets.append(tempTotal)
        self.table_widgets.append(tempActual)
        self.table_widgets.append(tempDiff)
        self.table_widgets.append(tempChange)
        #Display info
        for row in range(len(self.values_over_time[:20])):
            tempTotal = Label(self.mainFrame, text=self.values_over_time[row][0], borderwidth=2, relief="groove")
            tempTotal.grid(row=row + self.tableRow + 1, column=0, sticky=(N,S,E,W))
            tempActual = Label(self.mainFrame, text=self.values_over_time[row][1], borderwidth=2, relief="groove")
            tempActual.grid(row=row + self.tableRow + 1, column=1, sticky=(N,S,E,W))
            tempDiff = Label(self.mainFrame, text=self.values_over_time[row][2], borderwidth=2, relief="groove")
            tempDiff.grid(row=row + self.tableRow + 1, column=2, sticky=(N,S,E,W))
            tempChange = Label(self.mainFrame, text=self.values_over_time[row][3], borderwidth=2, relief="groove")
            tempChange.grid(row=row + self.tableRow + 1, column=3, sticky=(N,S,E,W))

            #Append items to list to delete later
            self.table_widgets.append(tempTotal)
            self.table_widgets.append(tempActual)
            self.table_widgets.append(tempDiff)
            self.table_widgets.append(tempChange)
            

            
#If running standalone
if __name__ == '__main__':        
    evaluator = stonks_evaluator()
