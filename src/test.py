import sys
import numpy as np
import pandas as pd
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

def printDataTable():  
   #read from disk
   print "------------ print table ---------------"
   df = pd.read_csv('yahoo_table.csv')
   print df
   print "------------ print table ---------------"
printDataTable()