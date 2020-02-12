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
                if pastDate >= earliestDate and current_row != 1:
                    starting_price = self.data_contents[current_row][company]
                    current_row-=1
                else:
                    acceptable_range = False

            #Get the price difference and append it
            increase = round(float(ending_price) - float(starting_price), 2)
            percentIncrease = round(((float(ending_price) / float(starting_price)) - 1) * 100, 2)
            retList.append([self.data_contents[0][company], increase, percentIncrease, round(float(starting_price), 2), round(float(ending_price), 2)])

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
        
    
