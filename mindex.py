from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import getopt
import sys
import math
import matplotlib.pyplot as plt
from termcolor import colored
from datetime import datetime

#TODO: improve graph readability, fix equality check for last value
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

#whether to show all stocks
all = False
#whether to show last price
#default is previous close
la = False

#for print color
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

def alignPrint(rows):
    # Build up a max length of each column
    lengths = {}
    for row in rows:
        for i in range(len(row)):
            lengths[i] = max(lengths.get(i, 0), len(row[i]))

    for row in rows:
        # For each cell, padd it by the max length
        output = ""
        for i in range(len(row)):
            if len(output) > 0:
                # Add a space between columns
                output += " "
            cell = row[i] + " " * lengths[i]
            cell = cell[:lengths[i]]
            output += cell
        print(output)

def parseDT(str):
    format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.strptime(str.rstrip(),format)

#flags
try:(lst,args) = getopt.getopt(sys.argv[1:],"halg",["help =","all =","last =","graph ="])
except:print("Error parsing flags")
for (opt,val) in lst:
    if opt in ['-h','--help']:
        rows = [
            ["-a", "--all",   "Print all tickers."],
            ["-l", "--last",  "Compute change based on last index value."],
            ["-g", "--graph", "Show a graph of past index values."],
            ["-h", "--help", "Print help message and exit."]
        ]
        alignPrint(rows)
        print("Warning: last only affects the index value")
        exit()
    if opt in ['-a','--all']:
        all = True
    if opt in ['-l','--last']:
        la = True
    if opt in ['-g','--graph']:
        with open ('index.csv','r') as file:
            xAxis = []
            yAxis = []

            for line in file.readlines():
                (value,dt) = line.split(maxsplit=1)
                dt=parseDT(dt)

                xAxis.append(dt.timestamp())
                yAxis.append(math.floor(float(value)))

            plt.plot(xAxis, yAxis)
            plt.show()

#get last index value
save = open('index.csv','r')
vals = save.readlines()
(l,d,t) = (vals[len(vals)-1]).split()
day = d
last = float(l)
save.close()

#get info and process it
def process(row: str):
    (symbol,weight) = row.split()
    w = float(weight)
    price=yf.Ticker(symbol).fast_info.last_price
    prev=yf.Ticker(symbol).fast_info.previous_close

    aux(price,prev)
    net = abs(price-prev)
    perc = (net/prev)*100
    #shows big changes
    threshold = 5 #>5% change

    if(perc>threshold or all):print (colored(symbol + ": " + str(price) + "\n" + arrow + str(net) + arrow + str(perc) + "%",color))

    #update indexes
    global index
    index+=(price*w)
    if la:
        global prevs
        prevs+=(prev*w)

#multithread it
with ThreadPoolExecutor() as executor:
    executor.map(process, tickers)

#adds value to index.csv
if(not last == index):
    save = open('index.csv','a')
    save.write(str(index) + " " + str(datetime.now()) + "\n")
    save.close()

#inefficient, add clamps so we don't unnecessarily compute prevs
if la: pr = prevs
else: pr = last
aux(index,prevs)
print(colored("Morgan's Brokerage Index: " + str(index/100) + "\n" + arrow + str(abs(index/100-pr/100)) + arrow + str((abs(index-pr)/pr)*100) + "%",color))
