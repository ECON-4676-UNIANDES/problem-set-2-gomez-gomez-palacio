from numpy.core.fromnumeric import shape
import sklearn
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import seaborn as sns
from shapely.geometry import Point, LineString
import multiprocessing
import matplotlib.pyplot as plt
import haversine
import pickle
import pysal 
from pysal.lib import weights
import libpysal as lps
from spreg import ml_lag
import spreg


#this models had future, unfortunately they did not converge.

########################################################################

# edificios:

with open('./aux_data/tidy_edificios.pkl', 'rb') as f:
    edificios = pickle.load(f)


edificios = edificios.loc[:,edificios.isna().sum() != len(edificios.index)]


edificios = edificios.dropna()

filt = []
for i in range(len(edificios.columns)):
    if np.all(edificios.iloc[0,i] == edificios.iloc[:,i]):
        filt.append(False)
    else: 
        filt.append(True)

edificios = edificios.loc[:,filt]
# project in a flat plane

par = edificios.to_crs({'init': 'epsg:3310'}).loc[:,['geometry']]

par.reset_index(drop = True, inplace = True)


# this finds the minimum threshold at which all parcels have at least one 
# neighboor, it is extremely intensive in memory 50Gb + use it wisely

def multiprocessing_func(n):
    w =  (
       weights.
       distance.
       DistanceBand.
       from_dataframe(
           par, 
           n, 
           binary=True
           )
        ).weights

    counter = 0 
    for i in w.keys():
        if sum(w[i]) == 0:
            counter += 1
    q.put([n,counter])
        

if __name__ == '__main__':
    q = multiprocessing.Queue()  
    processes = []
    for i in [i for i in range(407, 410)]:
        p = multiprocessing.Process(target=multiprocessing_func, 
                                    args=(i,))
        processes.append(p)
        p.start()
    
    
    
    resultado = []    
    for process in processes:
        a = q.get()
        resultado.append(a)
    for process in processes:
        process.join()
    

aux = [i[0] if i[1] == 0 else 8009000 for i in resultado]

########################################################################


w =  (
   weights.
   distance.
   DistanceBand.
   from_dataframe(
       par, 
       409, 
       binary=False
       )
    )

cols = [i for i in edificios.columns if i not in ['AssessedValue_l', 'geometry']]
X = np.asarray(edificios.loc[:,cols])
Y = np.asarray(edificios.loc[:,'AssessedValue_l'])


spreg.ml_lag.ML_Lag(Y.reshape((len(edificios.index)), 1), X,w )

########################################################################
# se hace lo mismo para los lotes 


with open('./aux_data/tidy_lotes.pkl', 'rb') as f:
    lotes = pickle.load(f)


lotes = lotes.loc[:,lotes.isna().sum() != len(lotes.index)]


lotes = lotes.dropna()

filt = []
for i in range(len(lotes.columns)):
    if np.all(lotes.iloc[0,i] == lotes.iloc[:,i]):
        filt.append(False)
    else: 
        filt.append(True)

lotes = lotes.loc[:,filt]
# project in a flat plane

par = lotes.to_crs({'init': 'epsg:3310'}).loc[:,['geometry']]

par.reset_index(drop = True, inplace = True)


# this finds the minimum threshold at which all parcels have at least one 
# neighboor, it is extremely intensive in memory 50Gb + use it wisely

def multiprocessing_func(n):
    w =  (
       weights.
       distance.
       DistanceBand.
       from_dataframe(
           par, 
           n, 
           binary=True
           )
        ).weights

    counter = 0 
    for i in w.keys():
        if sum(w[i]) == 0:
            counter += 1
    q.put([n,counter])
        

if __name__ == '__main__':
    q = multiprocessing.Queue()  
    processes = []
    for i in [i for i in range(400, 410)]:
        p = multiprocessing.Process(target=multiprocessing_func, 
                                    args=(i,))
        processes.append(p)
        p.start()
    
    
    
    resultado = []    
    for process in processes:
        a = q.get()
        resultado.append(a)
    for process in processes:
        process.join()
    

aux = [i[0] if i[1] == 0 else 8009000 for i in resultado]

########################################################################


w =  (
   weights.
   distance.
   DistanceBand.
   from_dataframe(
       par, 
       414, 
       binary=False
       )
    )

cols = [i for i in lotes.columns if i not in ['AssessedValue_l', 'geometry']]
X = np.asarray(lotes.loc[:,cols])
Y = np.asarray(lotes.loc[:,'AssessedValue_l'])


spreg.ml_lag.ML_Lag(Y.reshape((len(lotes.index)), 1), X,w )