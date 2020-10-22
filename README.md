# Problem set 2 
### By: Gómez x2 & Palacio

*Introduction* Hold on to your seat. In the following pages, we are going to tell you about a thing that ourselves just read about a couple of hours ago thanks to the help of dozens of cups of coffee ☕.

## Table of contents
- [Theoretical excercises ✍️](#features)
- [Empirical problems](empiricos/)
  - [Data](#data)
  - [1. Maps gomelos 📍](#1-maps-gomelos)
  - [2. Out of sight, but not out of mind 📈](#add-your-own-content)
  - [Scripts](empiricos/)

## Data
We used geographic data from the city of Evanston, a city in the Chicagoland area to graph our maps. the description of the files used is presented below (the names of the files are self-explanatory):
* **cblock.zip**: a compressed shapefile that contains 777 geometry entities corresponding to city blocks.
* **ctract.zip**: a compressed shapefile with the information of the population census divided into 18 territory divisions. Each one of that division aggregate many blocks.
* **El Lines.zip**: also known as the "The Purple Line of the Chicago". El Lines contains the geographic information of the metro line.
* **El Stations.zip**: 11 points corresponding to El's train stations
* **evanston.zip**: the geographic polygon of the city. We don't use this data. We have an ace up our sleeve. 
* **evanston_parcel_data.csv**: a CSV file that contains the information of 22.339 parcels in Evanston city. Some variables included are: Land Square Feet, Rooms, Bedrooms, Age, Total Building Square Feet, etc. 
* **Lake Michigan.zip**: geographic polygon of the Lake Michigan.
* **Major Roads.zip**: geographic lines correspondig to the principal avenues of the city. 
* **Metra Stops.zip**: Metra is the commuter rail system that serves the greater Chicago area. The Union Pacific North Line (UP-N), which connects Chicago’s northern suburbs to downtown Chicago, has stops at Main, Davis, and Central in Evanston. This compressed files contains 3 points.
* **Rail Lines.zip**: geographic lines correspondig to the rail lines. 

Also, we use external files from the [Open Data website of the Evanston city](data.cityofevanston.org) to enrich our models:
* **Beaches.zip**.
* **city.zip**: Enhanced shapefile from Evanston. The geographical borders are updated.
* **parcels_melo.pkl**: Clean version of evanston_parcel_data.csv.
* **tracts.zip**: Enhanced shapefile from tracts. The geographical borders are updated.
* **Trees.zip**.
* **Water bodies.zip**.
* **bici.geojson**: The City of Evanston has approximately 45 miles of protected bike lanes, bike lanes, bike routes and off-street paths. This file contains the polylines of this circuit.
* **cw.geojson**: Geodatabase with points indication school crosswalks.
* **food.geojson**: List with the localization of 394 food establishments.
* [**Data on arrests**](https://data.cityofevanston.org/resource/25em-v4fn.geojson)

The principal data can be downloaded from [here](https://github.com/ECON-4676-UNIANDES/Problem_Sets/tree/master/Problem_Set2/data) and auxiliary data can be accessed [here](empiricos/aux_data/)

## 1. Maps gomelos
1. [Average assessment values](empiricos/Outputs/Average_assessment_values.html)
2. [Building area to floor ratio](empiricos/Outputs/Building_area_to_floor_ratio.html)

In those HTML files, the 3 red markers represent Metra stations, also, the red dashed lines show the rail line. The gray markers represent El Stations and blue dashed lines indicate the trace of the El lines. We noticed a few outliers on the building area to floor ratio. Those observations with a ratio above the 95 percentile were deleted, probably those correspond to buildings with many floors. Additionally, we saw that the properties near the beach are the most expensive.
