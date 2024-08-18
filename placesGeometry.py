import re
from latLon import LatLon

class PlacesGeometry:
    # Threshold constants for population and income
    POPULATION_THRESHOLD = 101.3
    INCOME_THRESHOLD = 60000
    MIN_INCOME_THRESHOLD = 50000

    def __init__(self, name: str, coords: list):
        """
        Initialize a PlacesGeometry object.

        :param name: The name of the place.
        :param coords: A list of tuples representing the coordinates of the place.
        """
        self.name = name
        self.coords = coords
        self.pop = None  # Population of the place, set later
        self.inc = None  # Median income of the place, set later
        self.charger_num = 0  # Number of chargers in the place
        self.charger_locs = []  # List of charger locations

    @staticmethod
    def parse_multipolygon(multipolygon_str: str):
        """
        Parse a multipolygon string to extract the coordinates.

        :param multipolygon_str: A string representing the multipolygon in WKT format.
        :return: A list of tuples where each tuple represents a coordinate (latitude, longitude).
        """
        # Find the outer boundary of the multipolygon
        matches = re.findall(r'\(\(\(([^)]+)\)\)\)', multipolygon_str)
        if not matches:
            return []

        # Extract and parse the coordinates
        outer_boundary_str = matches[0]
        coords = [
            tuple(map(float, coord.split())) for coord in outer_boundary_str.split(',')
        ]
        return coords

    @staticmethod
    def is_point_in_polygon(point: LatLon, polygon: list):
        """
        Determine if the point (latitude, longitude) is inside the polygon defined
        by a list of (latitude, longitude) vertices using the ray-casting algorithm.

        :param point: A LatLon object representing the point.
        :param polygon: A list of tuples representing the vertices of the polygon.
        :return: True if the point is inside the polygon, False otherwise.
        """
        if not polygon:
            return False

        y = point[0]
        x = point[1]
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    @staticmethod
    def find_county(point: LatLon, counties: list):
        """
        Find the county that contains the given point.

        :param point: A LatLon object representing the point.
        :param counties: A list of county objects.
        :return: The county object that contains the point, or None if not found.
        """
        for county in counties:
            if PlacesGeometry.is_point_in_polygon(point, county.coords):
                return county
        return None

    @staticmethod
    def identify_diversity_counties(counties_info: list):
        """
        Identify counties that meet the diversity criteria based on population and income.

        :param counties_info: A list of county objects.
        :return: A list of county objects that meet the diversity criteria.
        """
        print("Identifying diversity counties...")
        diversity_counties = []
        for county in counties_info:
            population = county.pop
            median_income = county.inc
            if (population is not None) and (
                (population < PlacesGeometry.POPULATION_THRESHOLD and median_income < PlacesGeometry.INCOME_THRESHOLD)
                or median_income < PlacesGeometry.MIN_INCOME_THRESHOLD
            ):
                diversity_counties.append(county)
        return diversity_counties

    @staticmethod
    def calculate_additional_chargers(counties: list):
        """
        Calculate the number of additional chargers needed for each county.

        :param counties: A list of county objects.
        :return: A list of county objects with updated charger numbers.
        """
        update_list = []
        print("Calculating additional chargers...")
        for county in counties:
            population = county.pop
            median_income = county.inc

            # Example formula: inverse relation to population and income
            population_factor = PlacesGeometry.POPULATION_THRESHOLD / max(population, 1)
            income_factor = PlacesGeometry.INCOME_THRESHOLD / max(median_income, 1)

            # Scale the number of additional chargers
            additional_chargers = min(2, int(population_factor + income_factor))
            county.charger_num = additional_chargers
            update_list.append(county)

        return update_list

    @staticmethod
    def find_remaining_counties(pois: list, counties: list):
        """
        Identify counties that do not have points of interest (POIs) and assign them a charger.

        :param pois: A list of POI dictionaries with latitude and longitude keys.
        :param counties: A list of county objects.
        :return: A list of remaining county objects with assigned chargers.
        """
        remaining = counties.copy()
        for poi in pois:
            lat = poi['latitude']
            lon = poi['longitude']
            county = PlacesGeometry.find_county(LatLon(lat, lon), counties)
            if county in remaining:
                remaining.remove(county)
        for county in remaining:
            county.charger_num = 1

        return remaining

    def __str__(self):
        """
        String representation of the PlacesGeometry object.
        """
        return f"{self.name} has a population of {self.pop} and a median income of {self.inc}"
