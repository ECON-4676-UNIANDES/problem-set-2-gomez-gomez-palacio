# Server py script to run this without GUI
# this script uses 


import geopandas as gpd
import pandas as pd
import numpy as np
import os
import seaborn as sns
from shapely.geometry import Point, LineString
import multiprocessing
import matplotlib.pyplot as plt
import haversine



# define parcels
parcels = pd.read_csv('./data/evanston_parcel_data.csv')

#extract geo data from parcels
polygon_geom = []
for i in range(len(parcels.index)):
    p = Point(parcels.loc[i,'Longitude'], parcels.loc[i,'Latitude'])
    polygon_geom.append(p)

aux_df = gpd.GeoDataFrame(
    index=parcels.index, crs = {'init': 'epsg:4326'}, 
    geometry= polygon_geom
    )



parcels = gpd.GeoDataFrame(parcels).merge(
    aux_df, left_index = True, right_index = True
    )

parcels = parcels.set_crs({'init': 'epsg:4326'})




# get all zip files from the main directory
main_data_list = []
for i in os.listdir('./data'): 
    if 'zip' in i:
        main_data_list.append(i)




# add all the files to a dictionary

# main_data -> m_d
m_d = {}
for i in main_data_list:
    m_d[i.replace('.zip', '')] = gpd.read_file(
        'zip://' + os.getcwd() + '/data/' + i
        )



d_l = [i for i in m_d.keys()]


# set projections

for i in d_l:
    if m_d[i].crs is None:
            m_d[i] = m_d[i].set_crs({"init" : "epsg:4326"})
    else:
            m_d[i] = m_d[i].to_crs({"init" : "epsg:4326"})

        


# other data that can be linked to parcels and that might help us to better
# predict the prices:



# arrest:

m_d['arrest'] = gpd.read_file(
    'https://data.cityofevanston.org/resource/25em-v4fn.geojson'
    )
m_d['arrest'] = m_d['arrest'][m_d['arrest'].city.eq('EVANSTON')]


m_d['arrest'] = m_d['arrest'][m_d['arrest'].loc[:,'geometry'].notna()]



# 
a_data_list = []
for i in os.listdir('./aux_data'): 
    if 'zip' in i:
        a_data_list.append(i)
a_d = {}
for i in a_data_list:
    a_d[i.replace('.zip', '')] = gpd.read_file(
        'zip://' + os.getcwd() + '/aux_data/' + i
        )

# all the data is in the correct projection

m_d = {**m_d, **a_d}

del(a_d, a_data_list)

#now we add the geosjon files

a_data_list = []
for i in os.listdir('./aux_data'): 
    if 'geojson' in i:
        a_data_list.append(i)
a_d = {}
for i in a_data_list:
    a_d[i.replace('.geojson', '')] = gpd.read_file(
        os.getcwd() + '/aux_data/' + i
        )




# Complete data set m_d

m_d = {**m_d, **a_d}

# data list 
d_l = [i for i in m_d.keys()]

########################################################################
# filter cw to be a proxy for schools

m_d['cw'] = m_d['cw'].loc[
    [True if i in ['School Crossing Guard', 'Other School Crossing'] else False 
    for i in m_d['cw']['crosswalktype']],
    :
    ]

m_d['cw'].reset_index(drop = True, inplace = True)



########################################################################
## lake michigan does not have a defined shoreline:

# improve the lake Michigan
miny = (m_d['Water bodies'].
    loc[m_d['Water bodies']['name'].
    eq('Lake Michigan'), :].
    bounds['miny'].
    iloc[0]
)

bounds = list(
    m_d['Water bodies'].
    loc[m_d['Water bodies']['name'].
    eq('Lake Michigan'), :].
    boundary.
    iloc[0].
    coords
    )

line_min = []
for i in bounds:
    if abs(i[1] - miny) < 0.0001:
        line_min.append(i)

lon_min_left = np.array([i[0] for i in line_min]).argmin()
lon_min_right = np.array([i[0] for i in line_min]).argmax()


maxy = (
    m_d['Water bodies'].
    loc[m_d['Water bodies']['name'].
    eq('Lake Michigan'), :].
    bounds['maxy'].
    iloc[0]
)

line_max = []
for i in bounds:
    if abs(i[1] - maxy) < 0.0001:
        line_max.append(i)


lon_max_left = np.array([i[0] for i in line_max]).argmin()
lon_max_right = np.array([i[0] for i in line_max]).argmax()



vertices = [
    tuple(line_max[lon_max_left]),
    tuple(line_min[lon_min_left])
]
counter = len(bounds) - 1 
status = False
result = []
while True:
    if status:

        result.append(bounds[counter])
        if bounds[counter] in vertices:
            break

    else:
        if bounds[counter] in vertices:

            status = True
            result.append(bounds[counter])
    
    counter -= 1 

lon = [i[0] for i in result]
lat = [i[1] for i in result]
polygon_geom = LineString(zip(lon, lat))
crs = {'init': 'epsg:4326'}
m_d['Lake Michigan'] = gpd.GeoDataFrame(
    index=[0], crs=crs, geometry=[polygon_geom]
    ) 



#coords for shoreline
lake = list(m_d['Lake Michigan'].geometry.iloc[0].coords)  

#we need to add the lagoon which is located here
lagoon = list(m_d['Water bodies'].
    loc[m_d['Water bodies']['name'].
    eq('Northwestern Lagoon'), :].
    boundary.iloc[0].
    coords
    )

aux_c = []
aux_p = []
for p,i in enumerate(lake):
    if i in lagoon: 
        aux_c.append(i)
        aux_p.append(p)

#find the points in the lagoon:

lag = [] 
for p,i in enumerate(lagoon):
    if i in aux_c:
        lag.append(p)

#break the lake by the points
# new lagoon
nl = []
#first element : lagoon[lag[0] -1 ]
#last element : lagoon[lag[1] + 1 ]
#order : negative! 

counter = lag[0] - 1
itera = 0 
while counter!= lag[1] - len(lagoon):
    nl.append(lagoon[counter])
    counter -= 1

## now we add the things
result = lake[0:aux_p[0] + 1] + nl + lake[aux_p[1]:]

lon = [i[0] for i in result]
lat = [i[1] for i in result]
polygon_geom = LineString(zip(lon, lat))
crs = {'init': 'epsg:4236'}
m_d['Lake Michigan'] = gpd.GeoDataFrame(
    index=[0], crs=crs, geometry=[polygon_geom]
    ) 


########################################################################
# graph 1


fig, ax = plt.subplots(figsize = (6,8))

# base
m_d['city'].plot(ax = ax, color = "#999999")

#census tracts

m_d['tracts'].plot(
    ax = ax,
    column = 'name10',
    cmap = "Set2",
    categorical= True
    )

#census blocks

m_d['cblock'].geometry.boundary.plot(
    ax = ax, 
    label='blocks', 
    color = '#5840d4', 
    linewidth = 0.5
    )

#include beaches
m_d['Beaches'].plot(
    ax= ax, color = 'yellow'
    , label = "Beaches"
    )


#Major roads
m_d['Major Roads'].plot(
    ax = ax, 
    color = 'black'
    , label = "Main roads"
    )

# Rail Roads
# toca cambiar esto porque sale todo 
m_d['Rail Lines'].plot(
    ax = ax, 
    color = 'black', 
    linestyle= ':', 
    label = "Rail Lines", 
    marker = 'o'
    )


# Water bodies
m_d['Water bodies'].plot(
    ax=ax, 
    legend = True, 
    color = 'royalblue'
    )

# El Lines
m_d['El Lines'].plot(
    ax=ax, 
    color = 'red', 
    linestyle = 'dashdot', 
    label = 'El Lines'
    )

# El stations
m_d['El Stations'].plot(
    ax=ax, 
    color = 'darkgoldenrod', 
    label = 'El Stations'
    )

plt.ylim(42.015, 42.075)
plt.xlim(-87.75, -87.66)


#foo plots
plt.scatter([],[], marker = 'o', color = "royalblue", label = 'Water bodies')
plt.scatter([],[], marker = 'o', color = "yellow", label = 'Beaches')
plt.plot([],[], ' ', label = 'Census tracts \n in different colors')
plt.title('City of evanston')

plt.tick_params(
    axis='both',       
    which='both',      
    bottom=False,      
    top=False,         
    labelbottom=False,
    left =  False,
    labelleft = False) 


# plot and save
ax.legend(loc = 6)
plt.savefig('./plots/graph_1.png')
plt.close()








########################################################################






# match parcel data to block level file 

# find parcels outside of the city (defined as census tracts)

aux_0 = [
    i.replace('.', '') if '.' in i else i + '00' 
    for i in m_d['tracts'].name10.unique()
    ]


aux_1 = [str(i) for i in parcels['Census Tract'].unique()]
missing = [int(i) for i in [i for i in aux_1 if i not in aux_0]]

parcels = parcels.loc[
    [False if i in missing else True for i in parcels['Census Tract']],
    :
    ]

#restore index
parcels.reset_index(drop = True, inplace = True)


#now find blocks outside of the city (as we did with the parcels above)

aux_1 = [str(i) for i in m_d['cblock'].TRACT2000.unique()]
missing = [str(i) for i in [i for i in aux_1 if i not in aux_0]]
m_d['cblock'] = m_d['cblock'].loc[
    [False if i in missing else True for i in m_d['cblock'].TRACT2000],
    :
    ]

m_d['cblock'].reset_index(drop = True, inplace = True)


m_d['cblock']['TRACT2000'] = m_d['cblock']['TRACT2000'].apply(int)




# use multicore to do the separation:
# each core gets a part of the parcels (by tract)
# each core also gets the polygons corresponding to the blocks on that tract
# they have to keep the correct indexing to re assamble the data

# create a list [blocks, parcels] whithin a tract

complete_list = []

for i in m_d['cblock']['TRACT2000'].unique():
    complete_list.append([
        m_d['cblock'].loc[m_d['cblock']['TRACT2000'].eq(i), ['geometry', 'ID']],
        parcels.loc[parcels['Census Tract'].eq(i), ['geometry']] 
    ])

def check_where(parcel, tract):
    for i in tract.index: 
        if tract.loc[i,'geometry'].contains(parcel):
            return tract.loc[i, 'ID']
    return None

def multiprocessing_func(a_list):
    # unpack the list:
    tract = a_list[0]
    par = a_list[1]
    par['result'] = None
    for i in par.index:
        par.loc[i, 'result'] = check_where(par.loc[i,'geometry'],tract)
    q.put(par.loc[:,['result']])
    
if __name__ == '__main__':
    q = multiprocessing.Queue()  
    processes = []
    for i in complete_list:
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
        
# now join the results
marker = True
for i in resultado:
    if marker:
        marker = False
        result = i
    else:
        result = result.append(i)
    

# unpack result

result = result.sort_index()
result.rename(columns = {"result":"block"}, inplace = True)

#add column to parcels 

parcels = parcels.merge(result, left_index = True, right_index = True)

# find the block for the observations in parcels that did not have a block, 
# this are missmatched (their block is outside their tract which doesn't have 
# much sense)


a_list = [
    m_d['cblock'].loc[:, ['geometry', 'ID']] , 
    parcels.loc[[i is None for i in parcels.block], ['geometry']]
    ]

tract = a_list[0]
par = a_list[1]
par['result'] = None
for i in par.index:
    par.loc[i, 'result'] = check_where(par.loc[i,'geometry'],tract)



#the ratio is created

parcels['ratio'] = parcels['Building Square Feet']/parcels['Land Square Feet']


########################################################################



# create two aditional maps one for ratio and one for Assesed value


for i in ['ratio', 'Assessed Value'] :
    fig, ax = plt.subplots(figsize = (10,10))

# base
    m_d['city'].plot(ax = ax, color = "#999999")


    #census blocks

    (
        m_d['cblock'].
        merge(
            parcels.groupby('block').mean().loc[:,['Assessed Value', 'ratio']], 
            right_index = True, 
            left_on = "ID"
            ).plot(ax = ax, column = i, legend = True, cmap = 'binary')
    )


    #include beaches
    m_d['Beaches'].plot(ax= ax, color = 'yellow', label = "Beaches")


    #Major roads
    m_d['Major Roads'].plot(ax = ax, color = 'black', label = "Main roads")

    # Rail Roads
    # toca cambiar esto porque sale todo 
    m_d['Rail Lines'].plot(
        ax = ax, 
        color = 'black', 
        linestyle= ':', 
        label = "Rail Lines", 
        marker = 'o'
        )


    # Water bodies
    m_d['Water bodies'].plot(
        ax=ax, 
        legend = True, 
        color = 'royalblue'
        )

    # El Lines
    m_d['El Lines'].plot(ax=ax, 
    color = 'red', 
    linestyle = 'dashdot', 
    label = 'El Lines'
    )

    # El stations
    m_d['El Stations'].plot(
        ax=ax, 
        color = 'darkgoldenrod', 
        label = 'El Stations'
        )

    plt.ylim(42.015, 42.075)
    plt.xlim(-87.75, -87.66)

    #foo plots 
    plt.scatter(
        [],[], marker = 'o', color = "royalblue", label = 'Water bodies'
        )

    plt.scatter([],[], marker = 'o', color = "yellow", label = 'Beaches')

    plt.title('City of evanston')

    plt.tick_params(
        axis='both',       
        which='both',      
        bottom=False,      
        top=False,         
        labelbottom=False,
        left =  False,
        labelleft = False) 

    ax.legend(loc = 6)
    ax.legend(loc = 6)
    plt.savefig(f'./plots/{i}.png')
    plt.close()

########################################################################




#### create spatial variables:
# type 1: 
# minimum distance to:
    # Major Roads
    # Lake Michigan
    # Rail Lines
    # Metra Stops
    # El Lines
    # El Stations
    # Beaches 
    # bici
    # cw


def multiprocessing_func(a_list):

    parce, l_object, name = a_list
    parce = parce.to_crs({'init': 'epsg:3310'})
    l_object = l_object.to_crs({'init': 'epsg:3310'})
    
    def aux_fun(c_p):

        part_result = np.empty(len(l_object))

        for counter,c in enumerate(l_object.index):

            part_result[counter] = (
                l_object.loc[c,'geometry'].
                distance(c_p)
                )

        return part_result.min()


    for i in parce.index:
        current_parce = parce.loc[i,'geometry']

        parce.loc[i,'result'] = aux_fun(current_parce)
    
    q.put([parce.loc[:,['result']], name])







complete_list = []
vars = [
    'Major Roads',
    'Lake Michigan',
    'Rail Lines',
    'Metra Stops',
    'El Lines',
    'El Stations',
    'Beaches',
    'bici',
    'cw'
]

aux = np.linspace(0, len(parcels.index),65,dtype = int)
divi = []
prev = 0 
for i in aux[1:]:
    current_divi = [i for i in range(prev, i)]
    prev = i 
    divi.append(current_divi)


for t_o in vars: 
    for i in divi:
        complete_list.append([
            parcels.loc[i, ['geometry']],
            m_d[t_o].loc[:, ['geometry']], 
            t_o
        ])

if __name__ == '__main__':
    q = multiprocessing.Queue()  
    processes = []
    for i in complete_list:
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


# now join the results
ready = []
prov_dict = {}
for i in resultado:
    if i[1] in ready:
        prov_dict[i[1]] = prov_dict[i[1]].append(i[0])
    else:
        prov_dict[i[1]] = i[0]
        ready.append(i[1])

# now everything goes into parcels

for i in prov_dict.keys():
    prov_dict[i].rename({"result" : i}, inplace = True)
    parcels = parcels.merge( 
        prov_dict[i],
        right_index = True, 
        left_index = True, 
        how = 'left'
        )




########################################################################
# type 2: 
    # number of n in a radious of n meters

# def multiprocessing_func(a_list):

#     parce, l_object, name = a_list

#     parce['result'] = None

#     def aux_fun(c_p):
#         counter = 0
#         for c in l_object.index:
            
#             current_obj = (
#                     l_object.loc[c,'geometry'].coords.xy[1][0],
#                     l_object.loc[c,'geometry'].coords.xy[0][0],
#                 )

#             aux = haversine.haversine(
#                 current_obj, 
#                 c_p, 
#                 unit=haversine.Unit.METERS
#                 )
#             if aux < 200:
#                 counter += 1

#         return counter

#     for i in parce.index:
#         current_parce = (
#                             parce.loc[i,'geometry'].coords.xy[1][0],
#                             parce.loc[i,'geometry'].coords.xy[0][0],
#                         )

#         parce.loc[i,'result'] = aux_fun(current_parce)
    
#     q.put([parce.loc[:,['result']], name])


# # create a list for the different things that we need distance to:

# complete_list = []
# for t_o in ['Trees', 'arrest', 'food']: 
#     for i in m_d['cblock']['TRACT2000'].unique():
#         complete_list.append([
#             parcels.loc[parcels['Census Tract'].eq(i), ['geometry']],
#             m_d[t_o].loc[:, ['geometry']], 
#             t_o
#         ])


# if __name__ == '__main__':
#     q = multiprocessing.Queue()  
#     processes = []
#     for i in complete_list:
#         p = multiprocessing.Process(target=multiprocessing_func, 
#                                     args=(i,))
#         processes.append(p)
#         p.start()
    
    
    
#     resultado = []    
#     for process in processes:
#         a = q.get()
#         resultado.append(a)
#     for process in processes:
#         process.join()


# # now join the results
# ready = []
# prov_dict = {}
# for i in resultado:
#     if i[1] in ready:
#         prov_dict[i[1]] = prov_dict[i[1]].append(i[0])
#     else:
#         prov_dict[i[1]] = i[0]
#         ready.append(i[1])

# # now everything goes into parcels

# for i in prov_dict.keys():
#     prov_dict[i].rename({"result" : i}, inplace = True)
#     parcels = parcels.merge( 
#         prov_dict[i],
#         right_index = True, 
#         left_index = True, 
#         how = 'left'
#         )



