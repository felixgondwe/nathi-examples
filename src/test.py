import sys
import numpy as np
import pandas as pd
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import time




#custom example reading from local disk
def printDataTable():  
   #read from disk
   print "------------ print table ---------------"
   df = pd.read_csv('yahoo_table.csv')
   print df
   print "------------ print table ---------------"

###################### online example reading from yahoo finance ############

def readData(li_startDate,li_endDate,ls_symbols):
    #datetime object
    dt_start = dt.datetime(li_startDate[0],li_startDate[1],li_startDate[2])
    dt_end = dt.datetime(li_endDate[0],li_endDate[1],li_endDate[2])
    dt_timeofday = dt.timedelta(hours=14)
    ldt_timestamps = du.getNYSEdays(dt_start,dt_end,dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo',cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    return [d_data, dt_start, dt_end, dt_timeofday, ldt_timestamps]

def simulate(li_startDate, li_endDate, ls_symbols, lf_allocations, b_print):
    
    start = time.time();
    
    #Check if ls_symbols and lf_allocations have same length
    if len(ls_symbols) != len(lf_allocations):
        print "ERROR: Make sure symbol and allocation lists have same number of elements.";
        return;
    #Check if lf_allocations adds up to 1
    sumAllocations = 0;
    for x in lf_allocations:
        sumAllocations += x;
    if sumAllocations != 1:
        print "ERROR: Make sure allocations add up to 1.";
        return;

    #Prepare data for statistics
    x_data = readData(li_startDate, li_endDate, ls_symbols)
    print x_data
    d_data = readData(li_startDate, li_endDate, ls_symbols)[0];

    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;

    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];

    lf_Stats = calcStats(na_normalized_price, lf_allocations);

    #Print results
    if b_print:
        print "Start Date: ", li_startDate;
        print "End Date: ", li_endDate;
        print "Symbols: ", ls_symbols;
        print "Volatility (stdev daily returns): " , lf_Stats[0];
        print "Average daily returns: " , lf_Stats[1];
        print "Sharpe ratio: " , lf_Stats[2];
        print "Cumulative daily return: " , lf_Stats[3];

        print "Run in: " , (time.time() - start) , " seconds.";

    #Return list: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
    return lf_Stats[0:3]; 

def calcStats(na_normalized_price, lf_allocations):
    #Calculate cumulative daily portfolio value
    #row-wise multiplication by weights
    na_weighted_price = na_normalized_price * lf_allocations;
    #row-wise sum
    na_portf_value = na_weighted_price.copy().sum(axis=1);

    #Calculate daily returns on portfolio
    na_portf_rets = na_portf_value.copy()
    tsu.returnize0(na_portf_rets);

    #Calculate volatility (stdev) of daily returns of portfolio
    f_portf_volatility = np.std(na_portf_rets); 

    #Calculate average daily returns of portfolio
    f_portf_avgret = np.mean(na_portf_rets);

    #Calculate portfolio sharpe ratio (avg portfolio return / portfolio stdev) * sqrt(252)
    f_portf_sharpe = (f_portf_avgret / f_portf_volatility) * np.sqrt(250);

    #Calculate cumulative daily return
    #...using recursive function
    def cumret(t, lf_returns):
        #base-case
        if t==0:
            return (1 + lf_returns[0]);
        #continuation
        return (cumret(t-1, lf_returns) * (1 + lf_returns[t]));
    f_portf_cumrets = cumret(na_portf_rets.size - 1, na_portf_rets);

    return [f_portf_volatility, f_portf_avgret, f_portf_sharpe, f_portf_cumrets, na_portf_value];

startDate = [2016,1,1]
endDate = [2016,12,31]
simulate(startDate,endDate,['AAPL','MSFT','XOM'], [0.4, 0.4, 0.2], True)





