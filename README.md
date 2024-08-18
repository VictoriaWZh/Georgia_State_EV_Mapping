# Georgia State EV Mapping
Point clustering method to map EV stations in Georgia state

## Description
Team Sphere developed this program for the [ACM SIGSPATIAL Cup 2024](https://sigspatial2024.sigspatial.org/giscup/index.html), which focuses on the optimal minimum deployment of electric vehicle charging stations in Georgia state. The program analyzes key destinations, infrastructure availability, and socio-economic factors.

### Main Algorithm
The main algorithm used to place EV Charging stations is DBSCAN point-clustering. Given a CSV database of all location POIs and vehicle hotspots (e.g., parking, fuel, etc.) extracted from an OSM file, the data points were initially clustered for centroid latitude and longitude points. Then, the raw points were adjusted to the nearest vehicle POI and assigned a weight based on the popularity of the point. The ID became the name of the vehicle POI or attached an ambiguous name.

### Diversity and Finalizing
To ensure diversity across the state rather than localized in POI hotspots, county boundary, income, and population data were factored in. Based on a threshold, the program calculates the amount of additional chargers to accommodate "diversity" counties, and points are locally clustered within the county. Finally, the remaining counties without any chargers are found (via ray-casting) and clustered for thoroughness. The combined points are adjusted again and written into a GeoPackage file.

## Dependencies
Most modules are within the Python Standard Library, but all imported modules are within requirements.txt

## Authors
Victoria Zhang
