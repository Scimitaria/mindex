# mindex
A Python program which uses the yfinance library to create a custom brokerage index.

This program requires two supplemental files.

tickrs.csv should contain the amount of holdings that Yahoo Finance can't access on the first line, followed by weighted holdings:
```
50000
BTEAF 1000
GME 420
```

index.csv holds save data for past index values and their dates.
