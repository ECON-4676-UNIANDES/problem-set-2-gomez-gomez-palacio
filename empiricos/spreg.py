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
import pysal as ps
from pysal.lib import weights


with open('./aux_data/parcels.pkl', 'rb') as f:
    parcels = pickle.load(f)


# project in a flat plane

parcels = parcels.to_crs({'init': 'epsg:3310'})


def multiprocessing_func(n):
    w =  (
       weights.
       distance.
       DistanceBand.
       from_dataframe(
           parcels, 
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
    for i in [i for i in range(150,200)]:
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
    

results = np.array((50,2), dtype = int)

for i in range(50):
    results[i,:] = resultado[i]