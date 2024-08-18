import math
import random

class LatLon:
    def __init__(self, lat: float, lon: float):
        """
        Initialize a LatLon object with latitude, longitude, and an optional weight.
        
        :param lat: Latitude of the point
        :param lon: Longitude of the point
        """
        self.lat = lat
        self.lon = lon
        self.weight = None  # Weight initialized to None, to be set later if needed
    
    @staticmethod
    def find_point(points : list, lat : float, lon : float):
        """
        Find a point in a list of LatLon objects by matching latitude and longitude.
        
        :param points: List of LatLon objects
        :param lat: Latitude to search for
        :param lon: Longitude to search for
        :return: The matching LatLon object, or None if not found
        """
        for point in points:
            if point.get_lat() == lat and point.get_lon() == lon:
                return point
        return None
    
    @staticmethod
    def calculate_weight(num : int):
        """
        Calculate a weight based on the given number using a logarithmic formula, 14.
        
        :param num: The number to base the weight calculation on
        :return: Calculated weight as an integer
        """
        if num <= 87:
            return random.randint(1, 2)
        else:
            return min(int(round((math.log(num, 1000) * math.log(num ** 4, 10)) / 2)), 14)

    def get_lat(self):
        """Return the latitude of the point."""
        return self.lat
    
    def get_lon(self):
        """Return the longitude of the point."""
        return self.lon
        
    def get_weight(self):
        """Return the weight of the point, if set."""
        return self.weight
    
    def set_weight(self, weight : int):
        """
        Set the weight of the point.
        """
        self.weight = weight
    
    def __str__(self):
        """
        Return a string representation of the LatLon object.
        """
        return f"({self.lat}, {self.lon}) with a capacity of {self.weight}"
