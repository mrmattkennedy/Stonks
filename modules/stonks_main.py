import os
import sys
import time
import atexit
import datetime
import threading
import subprocess
import stonks_scraper
import stonks_analyzer
import stonks_visualizer
import tkinter.scrolledtext as tkst
from tkinter import *
from multiprocessing import Queue


class stonks_main:
    def __init__(self):
        #Make sure all modules installed
        self.module_list = ["matplotlib"]
        self.install_all_packages(self.module_list)

        #Initialize queue for thread return values
        self.messageQ = Queue()

        #Create GUI
        self.gui = Tk()
        self.gui.title('Stonks')
        self.total_cols = 3
        
        #Frame for scraper
        self.scraperFrame = Frame(self.gui, borderwidth=2, relief="ridge")
        self.scraperFrame.grid(row=0, column=0, sticky=(N,W,E))
        
        #Scraper widgets
        temp = Label(self.scraperFrame, text="Scraper output")
        temp.grid(row=0, column=0, sticky=(N,W))
        self.scraperOutput = tkst.ScrolledText(self.scraperFrame, width=60, height=5, state='disabled')
        self.scraperOutput.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=(S,E,W))
        self.scraperRunning = False
        self.blockingScraper = False
        self.running = True
        
        #Frame for analyzer
        self.analyzerFrame = Frame(self.gui, borderwidth=2, relief="ridge")
        self.analyzerFrame.grid(row=1, column=0, sticky=(W,E))
                
        #Analyzer widgets
        temp = Label(self.analyzerFrame, text="Analyzer output")
        temp.grid(row=0, column=0, sticky=(N,W))
        self.analyzerOutput = tkst.ScrolledText(self.analyzerFrame, width=60, height=5, state='disabled')
        self.analyzerOutput.grid(row=1, column=0, rowspan=2, columnspan=3, sticky=(S,E,W))

        #Frame for buttons
        self.buttonFrame = Frame(self.gui)
        self.buttonFrame.grid(row=2, column=0, sticky=(S,W,E))
        for col in range(self.total_cols):
            self.buttonFrame.grid_columnconfigure(col, weight=1, uniform="wide")

        #Button widgets
        self.scraperBtn = Button(self.buttonFrame, text="Scraper", command=self.start_scraper)
        self.scraperBtn.grid(row=0, column=0, columnspan=1, padx=3, pady=3, sticky=(N,S,W))
        self.analzyerBtn = Button(self.buttonFrame, text="Analyzer")
        self.analzyerBtn.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky=(N,S))
        self.visualizerBtn = Button(self.buttonFrame, text="Visualizer", command=self.start_visualizer)
        self.visualizerBtn.grid(row=0, column=2, columnspan=1, padx=3, pady=3, sticky=(N,S,E))

        #Initialize scraper object
        self.scraper = stonks_scraper.stonks_scraper()
        self.scraper.start()
        self.update_log(self.scraperOutput, "Started!")
        
        self.analyzer = stonks_analyzer.stonks_analyzer()
        self.update_log(self.analyzerOutput, "Started!")
        
        
        #Start gui, add exit handlers for key event (CTRL+C), or window close
        atexit.register(self.exit_handler)
        self.gui.protocol("WM_DELETE_WINDOW", self.exit_handler)
        self.gui.mainloop()
        
    #Loop through packages given, install necessary ones
    def install_all_packages(self, modules_to_try):
        for module in modules_to_try:
            try:
               __import__(module)
            except ImportError as e:
                self.install(e.name)

    #Helper function to install each package
    def install(self, package):
        try:
            subprocess.check_call(["python", '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError:
            print("Failed to install module " + package)
            print("Exiting. . .")
            exit

    """
    Scraper section.
    Starts a scraper thread, which will start a new scraper every 60 seconds
    """
    def start_scraper(self):
        if not self.scraperRunning and not self.blockingScraper:
            self.scraperRunning = True
            self.scraper_thread = threading.Thread(target=self.scraping_thread)
            self.scraper_thread.start()
            self.update_log(self.scraperOutput, "Initializing scraper master")
        else:
            if self.blockingScraper:
                return
            self.scraperRunning = False
            self.update_log(self.scraperOutput, "Stopping scraper master")
    
    def scraping_thread(self):
        while self.scraperRunning:
            #Start scraping thread
            #DO NOT ADD () ON TARGET FUNC, or it will run immediately and block on main thread
            self.update_log(self.scraperOutput, "Starting slave")
            self.scrape_data_thread = threading.Thread(target=self.scraper.get_prices, args=(self.messageQ,))
            self.scrape_data_thread.start()

            #Block until response. Redundancy in scraperRunning check
            #to see if main thread quit, preventing issue trying to write
            #to a gui that doesn't exist.
            while self.messageQ.empty() and self.scraperRunning:
                time.sleep(0.1)
            
            if self.scraperRunning:
                self.update_log(self.scraperOutput, "Iteration " + str(self.messageQ.get()) + " done")
                self.update_log(self.scraperOutput, "Took " + str(self.messageQ.get()) + " seconds")
                self.update_log(self.scraperOutput, "", addTimeStamp=False)

                #Having issues threading, try this.
                self.run_analyzer()

            else:
                self.update_log(self.scraperOutput, "Blocking until scraper threads done")
                self.blockingScraper = True
                self.messageQ.get()
                self.messageQ.get()
                self.blockingScraper = False
                self.update_log(self.scraperOutput, "Done blocking")
                
    def run_analyzer(self):
        self.analyzer = stonks_analyzer.stonks_analyzer()
        total_value, actual_value = self.analyzer.check_stocks()
        if self.scraperRunning:
            self.update_log(self.analyzerOutput, "Total value is " + str(round(float(total_value), 2)))
            self.update_log(self.analyzerOutput, "Actual value is " + str(round(float(actual_value), 2)))
            self.update_log(self.analyzerOutput, "Diff is " + str(round(float(actual_value) - float(total_value), 2)))
            self.update_log(self.analyzerOutput, "", addTimeStamp=False)
            
    """
    Visualizer section.
    Opens the visualizer. This is standalone so not much here.
    """
    def start_visualizer(self):
        system = os.name
        if system == 'nt': #Windows
            p = subprocess.Popen([sys.executable, sys.path[0] + "\\stonks_visualizer.py"])
        elif system == 'posix':
            p = subprocess.Popen([sys.executable, sys.path[0] + "//stonks_visualizer.py"], shell=True)


    #Updates the given widget (log) with the given text
    def update_log(self, widget, text, addTimeStamp=True):
        if self.running and addTimeStamp:
            widget.configure(state='normal')
            widget.insert("end", text + " @ " + datetime.datetime.now().time().strftime("%H:%M:%S") + "\n")
            widget.see(END)
            widget.configure(state='disabled')
        elif self.running:
            widget.configure(state='normal')
            widget.insert("end", text + "\n")
            widget.see(END)
            widget.configure(state='disabled')

    def exit_handler(self):
        self.scraperRunning = False
        self.running = False
        self.gui.destroy()
        exit


#If running standalone
if __name__ == '__main__':        
    driver = stonks_main()
