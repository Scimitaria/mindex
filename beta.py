import statistics

rm = [] #market return
ri = [] #security return

beta = statistics.covariance(ri,rm)/statistics.variance(rm)
print(beta)
