import statistics

#rm = market return
#ri = security return

def beta(rm,ri):
    return statistics.covariance(ri,rm)/statistics.variance(rm)
