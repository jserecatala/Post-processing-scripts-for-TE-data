# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 19:50:39 2018

@author: jr1n16
"""
import time
start_time = time.time() #start the clock

#Import libraries 
import pandas as pd
import numpy as np
from scipy import stats
#import matplotlib.pyplot as plt


#define a fuction for parabolic fit - joule fit
def joulefit(A, C, x):
    '''
    takes the fitting parameters A and C
    takes the temperature, x, as a list
    '''
    return A*x**2+C

#Load the data for thermometre 1&2 as well as for Voc
thermometre1 = pd.DataFrame(pd.read_csv("T1.txt", delim_whitespace=True, header=None, 
                              names=["T / K e", "T / K m", "I / mA", "V / mV"]))

thermometre2 = pd.DataFrame(pd.read_csv("T2.txt", delim_whitespace=True, header=None, 
                              names=["T / K e", "T / K m", "I / mA", "V / mV"]))

op_circ_volt = pd.DataFrame(pd.read_csv("Voc.txt", delim_whitespace=True, header=None, 
                              names=["T / K e", "T / K m", "I / mA", "V / mV"]))

n_steps = 1000 #define number of points of the parabolic fit
n_thermometre1 = int(len(thermometre1)/9) #equispaced the data to get the different temperatures 
n_thermometre2 = int(len(thermometre2)/9) #equispaced the data to get the different temperatures 
n_voc = int(len(op_circ_volt)/9) #equispaced the data to get the different temperatures 


list_df_t1 = [thermometre1[i*9:i*9+9] for i in range(0,n_thermometre1)] #split data into df't of I-V per thermom1
list_df_t2 = [thermometre2[i*9:i*9+9] for i in range(0,n_thermometre2)] #split data into df't of I-V per thermom2  
list_df_voc = [op_circ_volt[i*9:i*9+9] for i in range(0,n_voc)] #split data into df't of I-Voc per temp  

C1_list = []
T1_list = []
delta_R1_list = []
for temperature_df in list_df_t1:
    x = temperature_df["I / mA"].values
    y = temperature_df["V / mV"].values
    A, _, C = np.polyfit(x,y,deg=2)
    T_mean = temperature_df['T / K e'].mean()
    T1_list.append(T_mean)
    C1_list.append(C) #independent terms of parabola for thermometre 1
    x_fit = np.linspace(np.min(x), np.max(x), n_steps)
    y_fit = joulefit(A, C, x_fit)
    delta_R1_list.append(y_fit-C) #substract the independent term to parabola, brings down to 0

resistances_thermo1 = pd.DataFrame(C1_list, columns=["R1 / Ohm"])
temperatures_thermo1 = pd.DataFrame(T1_list, columns=["T / K"])

calibration_t1 = pd.concat([temperatures_thermo1, resistances_thermo1],axis=1)
calibration_t1.to_csv("Thermometer1.csv") #

#Resist_T1 = plt.scatter(T1_list, C1_list)
linear_fit_T1 = stats.linregress(T1_list,C1_list)
R_therm1 = linear_fit_T1.slope
T1 = [R1C/R_therm1 for R1C in delta_R1_list]


C2_list = []
T2_list = []
R2C_list = []
for temperature_df in list_df_t2:
    x = temperature_df["I / mA"].values
    y = temperature_df["V / mV"].values
    A, _, C = np.polyfit(x,y,deg=2)
    T_mean = temperature_df['T / K e'].mean()
    T2_list.append(T_mean)
    C2_list.append(C)
    
    x_fit = np.linspace(np.min(x), np.max(x), n_steps)
    y_fit = joulefit(A, C, x_fit)
    R2C_list.append(y_fit-C)
   
resistances_thermo2 = pd.DataFrame(C2_list, columns=["R2 / Ohm"])
temperatures_thermo2 = pd.DataFrame(T2_list, columns=["T / K"])

calibration_t2 = pd.concat([temperatures_thermo2, resistances_thermo2],axis=1)
calibration_t2.to_csv("Thermometer2.csv")  
    
    
linear_fit_T2 = stats.linregress(T2_list,C2_list)
R_therm2 = linear_fit_T2.slope
T2 = [R2C/R_therm2 for R2C in R2C_list]

new_DT = []
for (e1,e2) in zip(T1,T2):
    new_DT.append(e1-e2)
    
delta_T = pd.DataFrame(new_DT)

t_DT = delta_T.transpose()

fitted_current = pd.DataFrame(x_fit)

combined = pd.concat([fitted_current, t_DT], axis=1)

combined.to_csv("DeltaT.csv")  


VOC_list = []
for temperature_df in list_df_voc:
    x = temperature_df["I / mA"].values
    y = temperature_df["V / mV"].values
    A, _, C = np.polyfit(x,y,deg=2)    
    x_fit = np.linspace(np.min(x), np.max(x), n_steps)
    y_fit = joulefit(A, C, x_fit)
    VOC_list.append(y_fit)

S_list = []
for i in range(len(VOC_list)):
    linear_fit = stats.linregress(new_DT[i],VOC_list[i])
    S_list.append(linear_fit.slope)

temperatures = pd.DataFrame(T1_list)
Seebeck_coefs = pd.DataFrame(S_list)

analysed_data = pd.concat([temperatures, Seebeck_coefs], axis=1)
analysed_data.to_csv("Seebeck_coeff.csv")


print("Runtime = %s seconds" % (time.time() - start_time))
