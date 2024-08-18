import csv
from latLon import LatLon
from poi import Poi
from placesGeometry import PlacesGeometry

class CSVAnalysis:
    def __init__(self, path: str):
        """Initialize with the path to the CSV file."""
        self.path = path

    @staticmethod
    def create_dicts(points: list):
        """Convert a list of points (longitude, latitude) into a list of dictionaries with 'latitude' and 'longitude' keys."""
        print("Extracting latitude and longitude from points...")
        lat_lons = []
        for point in points:
            coord_dict = {
                "latitude": point[1],
                "longitude": point[0]
            }
            lat_lons.append(coord_dict)
        
        return lat_lons

    def read_points(self):
        """Read points from the CSV file and convert them into a list of Poi objects."""
        pois = []
        # Open the file with UTF-8 encoding, ignoring errors
        with open(self.path, encoding='utf-8', errors='ignore') as csv_file:
            csv_reader = csv.reader(csv_file)
            print("Reading CSV file for points...")
            next(csv_reader)  # Skip the header row
            for line in csv_reader:
                # Create LatLon and Poi objects from the CSV data
                point = LatLon(float(line[4]), float(line[5]))
                poi = Poi(line[3], line[2], point)
                pois.append(poi)
        
        return pois
    
    def create_lat_lons(self):
        """Extract latitude and longitude from Poi objects and return a list of dictionaries."""
        pois = self.read_points()
        print("Extracting latitude and longitude from Poi objects...")
        lat_lons = []
        for poi in pois:
            coord_dict = {
                "latitude": poi.getPoint().getLat(),
                "longitude": poi.getPoint().getLon()
            }
            lat_lons.append(coord_dict)
        
        return lat_lons
    
    def raw_points(self):
        """Extract raw LatLon objects from Poi objects and return them as a list."""
        pois = self.read_points()
        lat_lons = [LatLon(poi.getPoint().getLat(), poi.getPoint().getLon()) for poi in pois]
        return lat_lons

    def read_places(self, population_path: str, income_path: str):
        """Read geographic places from a CSV file and enrich them with population and income data."""
        places = []
        
        # Read places and their geometries from the primary CSV file
        with open(self.path, encoding='utf-8', errors='ignore') as csv_file:
            csv_reader = csv.reader(csv_file)
            print("Reading coordinate file for places...")
            next(csv_reader)  # Skip the header row
            for line in csv_reader:
                if line[3] == "county":
                    coords = PlacesGeometry.parse_multipolygon(line[0])
                    county = PlacesGeometry(line[5], coords)
                    places.append(county)

        # Add population data from the population CSV file
        print("Reading population data...")
        with open(population_path, encoding='utf-8', errors='ignore') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row
            for line in csv_reader:
                for county in places:
                    if line[0] == county.name:
                        county.pop = float(line[1])
                    
        # Add income data from the income CSV file
        print("Reading income data...")
        with open(income_path, encoding='utf-8', errors='ignore') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row
            for line in csv_reader:
                for county in places:
                    if line[0] == county.name:
                        county.inc = int(line[1])

        return places
