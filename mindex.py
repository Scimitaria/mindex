from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import csv
import getopt
import sys
from termcolor import colored
from datetime import datetime, timedelta
#yesterday = datetime.now()-timedelta(days=1)
#y = yesterday.strftime('%Y-%m-%d')
#TODO: add graph, report high/low earners
with open('tickrs.csv','r') as file:
    items = file.readlines()
    base = items[0]
    tickers = items[1:]

color = ''
arrow = ""

#represents holdings yfinance doesn't have access to
#bonds, core position, etc
index = float(base)
prevs = index

all = False
la = False

def aux(one: float, two: float):
    global color
    global arrow
    if  (one<two):
        color = 'red'
        arrow = "   v "
    elif(one>two):
        color = 'green'
        arrow = "   ^ "
    else: 
        color = 'white'
        arrow = "no change "

try:
    (lst,args) = getopt.getopt(sys.argv[1:],"hal",["help =","all =","last ="])
except:
    print("Error parsing flags")
for (opt,val) in lst:
    if opt in ['-h','--help']:
        print("help")
    if opt in ['-a','--all']:
        all = True
    if opt in ['-l','--last']:
        la = True

def process(row: str):
    (symbol,weight) = row.split()
    price=yf.Ticker(symbol).fast_info.last_price
    prev=yf.Ticker(symbol).fast_info.previous_close
    aux(price,prev)
    net = abs(price-prev)
    perc = (net/prev)*100
    threshold = 0
    if(perc>threshold and all):print (colored(symbol + ": " + str(price) + "\n" + arrow + str(net) + arrow + str(perc) + "%",color))
    global index
    global prevs
    index+=(price*float(weight))
    prevs+=(prev*float(weight))

with ThreadPoolExecutor() as executor:
    executor.map(process, tickers)

save = open('index.csv','r')
vals = save.readlines()
(l,d,t) = (vals[len(vals)-1]).split()
last = float(l)
save.close()
if(not last == index):
    save = open('index.csv','a')
    save.write(str(index) + " " + str(datetime.now()) + "\n")
    save.close()

#inefficient, add clamps so we don't unnecessarily compute last/prevs
if la: pr = prevs
else: pr = last
aux(index,prevs)
print(colored("Morgan's Brokerage Index: " + str(index/100) + "\n" + arrow + str(abs(index/100-pr/100)) + arrow + str((abs(index-pr)/pr)*100) + "%",color))