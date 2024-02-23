import time
import requests
import pandas as pd
from io import StringIO
from tqdm.auto import tqdm
from bs4 import BeautifulSoup


headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,zh;q=0.6"
}

session = requests.Session()
session.headers = headers


def saveSym(exchange, outputFile=None):
	exchanges = {
	"nasdaq": "https://www.advfn.com/nasdaq/nasdaq.asp?companies={letter}",	
	"nyse": "https://www.advfn.com/nyse/newyorkstockexchange.asp?companies={letter}",
	"amex": "https://www.advfn.com/amex/americanstockexchange.asp?companies={letter}"}

	url = exchanges[exchange.lower()]
	file = StringIO() \
		if outputFile is None \
		else open(outputFile, 'w', encoding="utf-8")
	file.write("symbol%name%urlStockPrice%urlChart%urlNews%urlFinancials%urlTrades\n")

	# advfn web structures each symbol by letter
	letters = "ABCDEFGHIJKLMNOPQUSTUVWXYZ+"
	for letter in tqdm(letters):
		request_data = session.get(url.format(letter = letter))
		request_html = request_data.text
		soup = BeautifulSoup(request_html, 'html.parser')
		content = soup.find_all("table", {"class", "market tab1"})
		rows = content[0].find_all("tr")
		for i in range(2, len(rows)):
			td = rows[i].find_all("td")
			symbol = td[1].getText()
			name = td[0].getText()

			a = rows[i].find_all("a")
			href_stock_price = a[1]["href"]
			href_chart = a[2]["href"]
			href_news = a[3]["href"] if len(a) > 3 else ''
			href_financials = a[4]["href"] if len(a) > 4 else ''
			href_trades = a[5]["href"] if len(a) > 5 else ''
			if len(symbol) != 0:
				file.write(f"{symbol}%{name}%{href_stock_price}%{href_chart}%{href_news}%{href_financials}%{href_trades}\n")

		time.sleep(1)
	
	if outputFile is None:
		file.seek(0)
		df = pd.read_csv(file, sep='%')
		file.close()
		return df

	file.close()
	print(f"Finished extracting data for {exchange}. Data saved in {outputFile}")


if __name__ == '__main__':
	saveSym("nasdaq", "nasdaqsym.txt")
	saveSym("amex", "amexsym.txt")
	saveSym("nyse", "nysesym.txt")