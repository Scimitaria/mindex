import re

def to_float(str):
    if str[-1] == '%': return float(str[:-1])
    return float(str)
def is_ticker(ticker):
    return re.fullmatch(r"[*A-Z:1-9.]+",ticker)
def is_percent(pct):
    return re.fullmatch(r"^-?\d+\.\d+\%?",pct)
def compute_pct(amt,tot):
    return float(amt)/tot

def read_dict(path,ticker_index=0,pct_index=-1,total=None):
    holdings={}
    with open(path) as f: items = f.readlines()
    for str in items:
        line = str.split()
        try:
            ticker = line[ticker_index]
            pct = compute_pct(line[pct_index],total) if total else line[pct_index]
        except IndexError:
            #if line is formatted incorrectly, it's not a holding
            continue
        if not (is_ticker(ticker) and is_percent(pct)): 
            #print(ticker,pct)
            #print(is_ticker(ticker),is_percent(pct))]
            continue
        holdings[ticker]=to_float(pct)
    return holdings

overlap = 0.0
overlapping_holdings = 0
computed=[]
fund1 = read_dict('overlap/FBGRX.txt',-4,-5)
fund2 = read_dict('overlap/PAGRX.txt',0,1)

for ticker,pct in fund1.items():
    if ticker in fund2:
        overlap += min(fund1[ticker],fund2[ticker])
        overlapping_holdings += 1
        computed.append(ticker)
for ticker in computed: del fund1[ticker],fund2[ticker]
for ticker,pct in fund2.items():
    if ticker in fund1:
        overlap += min(fund1[ticker],fund2[ticker])
        overlapping_holdings += 1
print(f"Overlap: {overlap:g}%")
print("Overlapping holdings: %d" % overlapping_holdings)
