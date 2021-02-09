# -*- coding: utf-8 -*-
"""
@author: jr1n16
"""
import time
import pandas as pd
import numpy as np
from scipy import stats
#import matplotlib.pyplot as plt

start_time = time.time() #start the clock

#define geometric parameters for the sample
thickness_sample = 0.00017 #writer here thickness of your sample in cm
thickness_ito = 0 #thickness of ITO in cm
total_thickness = thickness_ito + thickness_sample
width = 0.0964 #write here the width of the sample in cm
length = 0.1

#Load the data
data = pd.DataFrame(pd.read_csv("IV.txt", delim_whitespace=True, header=None, 
                              names=["T / K", "I / A", "V / V"], index_col = False))

n = int(len(data)/41) #equispaced the data to get the I-V per temperature 

list_data = [data[i*41:i*41+41] for i in range(0,n)] #split data into df't of I-V per T  

list_RT = []
list_R = []
list_T = []
for temperature in list_data:
    X1 = np.array((temperature.iloc[:,1]))
    y1 = np.array((temperature.iloc[:,-1]))
    linear_fit = stats.linregress(X1,y1)
    m = linear_fit.slope
    T_mean = temperature['T / K'].mean()
    list_RT.append((T_mean, m))
    list_R.append(m)
    list_T.append(T_mean)



list_sigma = [length/(m*width*total_thickness) for m in list_R] # List comprehension
#plt.scatter(list_T, list_sigma)
#plt.show()
#plt.savefig('ST.jpg')

remeasITO_iv = pd.DataFrame(list_RT)
remeasITO_iv.to_excel("Resistance.xlsx")

sigma = pd.DataFrame(list_sigma)
av_temperatures = pd.DataFrame(list_T)

remeasITO_sigma = pd.concat([av_temperatures, sigma], axis=1)
remeasITO_sigma.to_excel("Conductivity.xlsx")


print("Runtime = %s seconds" % (time.time() - start_time))
    

