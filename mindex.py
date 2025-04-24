from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import getopt
import sys
import math
import matplotlib.pyplot as plt
from termcolor import colored
from datetime import datetime

with open('tickrs.csv','r') as file:
    items = file.readlines()
    base = items[0]
    tickers = items[1:]

color = ''
arrow = ""

#represents holdings yfinance doesn't have access to
#bonds, core position, etc
index = float(base)
prevcloseclose = index
#whether to show all stocks
all = False
#whether to show last price
#default is previous close
isLastPrice = False

epsilon = 0.0001

#for print color
def aux(one: float, two: float):
    global color
    global arrow
    if abs(one - two) > epsilon:
        if  (one<two):
            color = 'red'
            arrow = "   v "
        elif(one>two):
            color = 'green'
            arrow = "   ^ "
    else:
        color = 'white'
        arrow = " no change "

#prints an aligned grid
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

#parses datetime from string
def parseDT(str):
    format = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.strptime(str.rstrip(),format)
#different format
def parseDT2(str):
    format = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(str.rstrip(),format)

#finds distance between dates
def inRangeDT(d1,d2,diff):
    return ((abs(d2-d1)/86400)>diff)

#finds last label
def findLabel(lst):
    ret='2025-02-27 15:27:30'
    for i in range(len(lst)-1):
        e=lst[i]
        if not (e==''):ret=e
    return ret

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
        isLastPrice = True
    if opt in ['-g','--graph']:
        with open ('index.csv','r') as file:
            xAxis = [] #numbers for x axis
            yAxis = [] #numbers for y axis
            xTick = [] #labels for x axis
            rep = 0

            lines = file.readlines()
            for i in range(len(lines)):
                (value,dt) = lines[i].split(maxsplit=1)
                newDT=parseDT(dt).timestamp()#convert from string to float

                #convert previous label to float
                if(i>0):iprev = parseDT2(findLabel(xTick)).timestamp()
                else:iprev=0
                #min number of days since last label
                interval = 31

                #if far enough from previous label, add new label
                if inRangeDT(iprev,newDT,interval):xTick.append(dt.split('.')[0])
                else:xTick.append('')

                #add axis counters
                xAxis.append(newDT)
                yAxis.append(math.floor(float(value)))

                rep+=1

            #draw graph
            with plt.xkcd():
                plt.plot(xAxis, yAxis)
                #plt.xlabel#fill
                plt.xticks(xAxis,xTick)#display labels for x axis
            plt.get_current_fig_manager().full_screen_toggle()#open in fullscreen
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
    global prevclose
    prevclose+=(prev*w)

#multithread it
with ThreadPoolExecutor() as executor:
    executor.map(process, tickers)

#round to prevent equality check errors
index=round(index,2)

#adds value to index.csv
if(not last == index):
    save = open('index.csv','a')
    save.write(str(index) + " " + str(datetime.now()) + "\n")
    save.close()

if isLastPrice: other = prevclose
else: other = last
aux(index,other)

line1 = "Morgan's Brokerage Index:" + str(index/100) + "\n"
line2 = arrow + str(abs(index/100-other/100)) + arrow + str((abs(index-other)/other)*100) + "%"
print(colored(line1 + line2,color))
