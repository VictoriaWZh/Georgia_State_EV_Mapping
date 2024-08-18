from latLon import LatLon

class Poi:
    def __init__(self, name: str, type: str, pt: LatLon):
        self.name = name
        self.type = type
        self.pt = pt
    
    @staticmethod
    def find_poi(pois : list, lat : float, lon : float):
        for poi in pois:
            if poi.getPoint().getLat() == lat and poi.getPoint().getLon() == lon:
                return poi
        return None
    
    @staticmethod
    def count_occurrence(list, name):
        count = 0
        for val in list:
            if val == name:
                count += 1
        return count

    @staticmethod
    def correct_names(pois : list):
        count = 0
        occurred = []
        for poi in pois:
            count += 1
            if poi.getName() == "Unamed":
                poi.name = f"EV Station {count}"
            else:
                occurred.append(poi.getName())
                poi.name = poi.name + " " + str(Poi.count_occurrence(occurred, poi.name) + 1)
        return pois

    def getName(self):
        return self.name
    
    def getType(self):
        return self.type
    
    def getPoint(self):
        return self.pt
    
    def __str__(self):
        return f"{self.name} of type {self.type} at {self.pt}"
