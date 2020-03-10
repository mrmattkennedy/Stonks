import datetime

class stonks_sorter():
    def __init__(self, data_contents):
        self.data_contents = data_contents

        
    """
    Helper function
    Get the earliest date for the highest increase range
    """
    def get_earliest_date(self, greatestIncreaseRange):
        if greatestIncreaseRange == "Day": #day
            return datetime.datetime.today().date()
        elif greatestIncreaseRange == "Week": #week
            return (datetime.datetime.now() - datetime.timedelta(days=7)).date()
        elif greatestIncreaseRange == "1 Month": #month
            today = datetime.datetime.today().date()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth == 1:
                return datetime.datetime.today().date().replace(month=12,year=currentYear-1)
            else:
                return datetime.datetime.today().date().replace(month=currentMonth-1)
        elif greatestIncreaseRange == "6 Months": #6 months
            today = datetime.datetime.today()
            currentMonth = today.month
            currentYear = today.year
            
            if currentMonth <= 7:
                return datetime.datetime.today().date().replace(month=12+(currentMonth-6),year=currentYear-1)
            else:
                return datetime.datetime.today().date().replace(month=currentMonth-6)
        elif greatestIncreaseRange == "Year": #year
            currentYear = datetime.datetime.today().year
            return datetime.datetime.today().date().replace(year=currentYear-1)

        return ""

    """
    Helper function
    Get list of greatest increases of stocks in data
    """
    def get_increase_list(self, length, earliestDate, growthDirectionVar, growthVar):
        retList = []
        for company in range(0, len(self.data_contents[0]), 2):
            startingPrice, endingPrice, increase, percentIncrease = self.get_price_diff(company, earliestDate)
            retList.append([self.data_contents[0][company], increase, percentIncrease, startingPrice, endingPrice])

        #Sort list according to greatest increase
        if growthDirectionVar == "Increase" and growthVar == "$":
            retList = sorted(retList, key = lambda x: x[1])
        elif growthDirectionVar == "Increase" and growthVar == "%":
            retList = sorted(retList, key = lambda x: x[2])
        elif growthDirectionVar == "Decrease" and growthVar == "$":
            retList = sorted(retList, key = lambda x: x[1])
            retList.reverse()
        elif growthDirectionVar == "Decrease" and growthVar == "%":
            retList = sorted(retList, key = lambda x: x[2])
            retList.reverse()
        return retList[-length:]
        
    def get_price_diff(self, company, earliestDate=None, index=None):
        #Get the last recorded price value
        last_row = len(self.data_contents) - 1
        empty_row = True

        #print(self.data_contents[0][company])
        while empty_row:
            if not self.data_contents[last_row][company]:
                last_row-=1
                continue
            empty_row = False

        #Get the prices starting at the last recorded price value
        starting_price = -1
        ending_price = self.data_contents[last_row][company]

        if earliestDate:
            ending_row = last_row
            acceptable_range = True
            
            while acceptable_range:
                try:
                    pastDate = datetime.datetime.strptime(self.data_contents[ending_row][company+1], "%m/%d/%Y %H:%M:%S").date()
                except ValueError:
                    pastDate = datetime.datetime.strptime(self.data_contents[ending_row][company+1], "%m/%d/%Y %H:%M").date()

                #Get starting price
                if pastDate >= earliestDate and ending_row != 1:
                    starting_price = self.data_contents[ending_row][company]
                    ending_row-=1
                else:
                    acceptable_range = False
            
        elif index:
            starting_row = last_row
            ending_row = last_row - index if last_row - index >= 1 else 1
            starting_price = self.data_contents[ending_row][company]
            
        #Get the price difference and append it
        if starting_price == -1:
            starting_price = ending_price
            increase = 0
            percentIncrease = 0
        else:
            increase = round(float(ending_price) - float(starting_price), 2)
            percentIncrease = round(((float(ending_price) / float(starting_price)) - 1) * 100, 2)
        
        return round(float(starting_price), 2), round(float(ending_price), 2), increase, percentIncrease
