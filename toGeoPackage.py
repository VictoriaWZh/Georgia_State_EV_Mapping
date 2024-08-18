import geopandas as gpd
from shapely.geometry import Point

class ToGeoPackage:
    def __init__(self):
        self.data = None

    def extract_data(self, pois : list):
        print("Extracting data...")
        data = {}
        ids = []
        latitudes = []
        longitudes = []
        capacities = []
        for poi in pois:
            ids.append(poi.getName())
            latitudes.append(poi.getPoint().getLat())
            longitudes.append(poi.getPoint().getLon())
            capacities.append(poi.getPoint().getWeight())
        data['id'] = ids
        data['latitude'] = latitudes
        data['longitude'] = longitudes
        data['capacity'] = capacities
        self.data = data

    def write_file(self):
        # Create a GeoDataFrame
        geometry = [Point(lon, lat) for lon, lat in zip(self.data['longitude'], self.data['latitude'])]
        gdf = gpd.GeoDataFrame(self.data, geometry=geometry, crs="EPSG:4326")

        # Specify the path to the GeoPackage file
        gpkg_path = 'C:\\Users\\vzhang\\workplace\\EVMapping\\outputs\\ev_charging_stations_1_1_sphere.gpkg'

        # Write to the GeoPackage file
        gdf.to_file(gpkg_path, driver='GPKG')
        print(f"GeoPackage file saved as '{gpkg_path}'")

