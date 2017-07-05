from urllib import request
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout
import time
import json
import sys

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
req = request.Request("https://cex.io/api/last_price/BTC/USD", headers=headers)
SMOOTHING_FACTOR = 0.005

def main(delay, SMOOTHING_FACTOR, buy_threshold, sell_threshold):
	try:
		coins = 0
		simulatedCash = 20000
		ewma = float(json.loads(request.urlopen(req).read())["lprice"])
		startTime = time.time()
		purchasePrice = 0
		points = []
		raw_points = []
		req_data_collected = False

		while True:
			nextPrice = float(json.loads(request.urlopen(req).read())["lprice"])
			raw_points.append(nextPrice)
			ewma = (nextPrice * SMOOTHING_FACTOR) + ((1-SMOOTHING_FACTOR) * ewma)
			print(ewma)
			time.sleep(delay)
			points.append(ewma)

			if time.time() - startTime > 3600:
				with open('prices.csv','a') as f:
					f.write(time.asctime()+","+str(ewma)+";\n")
				req_data_collected = True
				startTime = time.time()

			if req_data_collected:
				if ewma-nextPrice > buy_threshold and coins == 0:
					simulatedCash -= nextPrice						#Consolidate this into a method later
					coins+=1
					purchasePrice = nextPrice
				elif coins == 1 and nextPrice - purchasePrice > sell_threshold:
					simulatedCash += nextPrice
					coins -= 1
					with open('tradelog.csv','a') as f:
						f.write(time.asctime()+","+str(nextPrice - purchasePrice)+";\n")
	except Exception as e:
		print(e)
		plot([Scatter(x=list(range(1,len(points))), y=points), Scatter(x=list(range(1,len(raw_points))), y=raw_points)])
		print('\nCash after run ending at '+time.asctime()+": "+str(simulatedCash))

main(int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))