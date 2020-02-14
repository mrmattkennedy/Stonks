import requests
from bs4 import BeautifulSoup
url='http://eoddata.com/stocklist/NYSE/A.htm'
page = requests.get(url)

soup = BeautifulSoup(page.text, 'html.parser')
table = soup.find("table", {"class": "quotes"})
stocks = table.findAll("tr")
symbols = []

token_start = 'onclick="location.href=' + "'/stockquote/NYSE/"
token_end = ".htm'"
#print(stocks[1])
for stock in stocks[1:]:
    str_stock = str(stock)
    symbols.append(str_stock[str_stock.find(token_start) + len(token_start):
                             str_stock.find(token_end)])
for symbol in symbols:
    print(symbol)
