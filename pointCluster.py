import numpy as np
import matplotlib.pyplot as plt
from placesGeometry import PlacesGeometry
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from collections import defaultdict
from latLon import LatLon
from poi import Poi

class PointCluster:
    def __init__(self, points: list = None):
        """
        Initialize the PointCluster with optional list of points.
        """
        self.points = points
        self.coords = None
        self.clusters = None
        self.unique_labels = None
        self.labels = None

    @staticmethod
    def haversine_distance(coord1: tuple, coord2: tuple) -> float:
        """
        Calculate the Haversine (great-circle) distance between two points.
        """
        return great_circle(coord1, coord2).meters
      
    @staticmethod
    def combine_clusters(cluster1: list, cluster2: list) -> np.ndarray:
        """
        Combine two clusters of points into a single set of coordinates.
        """
        print("Combining clusters...")
        coords1 = np.array([[poi['latitude'], poi['longitude']] for poi in cluster1])
        coords2 = np.array([[poi['latitude'], poi['longitude']] for poi in cluster2])
        all_coords = np.vstack((coords1, coords2))
        return all_coords

    @staticmethod
    def filter_close_points(points: list, threshold=0.02) -> list:
        """
        Filter points that are close to each other by grouping them into grid cells 
        and retaining a representative point for each cell.
        """
        print("Filtering points...")

        def get_grid_key(lat, lon, threshold):
            """
            Generate a grid key based on latitude and longitude for grouping points.
            """
            return (int(lat / threshold), int(lon / threshold))

        grid = defaultdict(list)
        
        # Group points by grid cells
        for point in points:
            key = get_grid_key(point['latitude'], point['longitude'], threshold)
            grid[key].append(point)
        
        # Select a representative point for each grid cell
        filtered_points = []
        for point_list in grid.values():
            condensed_point = point_list[0]
            condensed_point['weight'] = len(point_list)
            filtered_points.append(condensed_point)
        
        return filtered_points    

    @staticmethod
    def assign_weights(lat_lons: list, pois: list) -> list:
        """
        Assign weights to LatLon objects based on the provided list and match them 
        with corresponding POIs (Points of Interest).
        """
        print("Assigning Weights...")
        poi_list = []
        for val in lat_lons:
            point = LatLon(val['latitude'], val['longitude'])
            point.setWeight(LatLon.calculate_weight(val['weight']))
            poi = Poi.find_poi(pois, val['latitude'], val['longitude'])
            if isinstance(poi, Poi):
                poi = Poi(poi.name, poi.type, point)
                poi_list.append(poi)
        return poi_list    
    
    @staticmethod
    def extract_county_points(county: PlacesGeometry, points: list) -> list:
        """
        Extract points that fall within the bounding box of a given county.
        """
        county_points = county.coords
        if not county_points:
            return []

        # Determine the bounding box of the county
        min_lat = min(point[1] for point in county_points)
        max_lat = max(point[1] for point in county_points)
        min_lon = min(point[0] for point in county_points)
        max_lon = max(point[0] for point in county_points)

        # Filter points within the bounding box
        filtered_points = [
            point for point in points
            if min_lat <= point['latitude'] <= max_lat and min_lon <= point['longitude'] <= max_lon
        ]
        
        return filtered_points

    @staticmethod    
    def cluster_counties(counties: list, points: list) -> list:
        """
        Cluster points by counties using DBSCAN and assign chargers based on 
        identified clusters.
        """
        charger_list = PlacesGeometry.calculate_additional_chargers(
            PlacesGeometry.identify_diversity_counties(counties)
        ) if len(counties) > 5 else counties

        final = []
        for county in charger_list:
            county_points = PointCluster.extract_county_points(county, points)
            if not county_points:
                continue

            # Prepare coordinates for clustering
            coords = np.array([[poi['latitude'], poi['longitude']] for poi in county_points])
            kms_per_radian = 6371.0088
            epsilon = 500 / kms_per_radian  # 500 meters in radians

            # Perform DBSCAN clustering
            db = DBSCAN(eps=epsilon, min_samples=2, metric=PointCluster.haversine_distance).fit(coords)
            labels = db.labels_

            # Identify and store clusters
            unique_labels = set(labels)
            clusters = {}
            for k in unique_labels:
                if k == -1:
                    continue  # Skip noise points
                class_member_mask = (labels == k)
                cluster_coords = coords[class_member_mask]
                centroid = cluster_coords.mean(axis=0)
                clusters[k] = {
                    'size': len(cluster_coords),
                    'centroid': centroid,
                    'points': cluster_coords
                }

            # Sort clusters by size and assign charger locations
            sorted_clusters = sorted(clusters.values(), key=lambda c: c['size'], reverse=True)
            for c in charger_list:
                if c.name == county.name:
                    largest_clusters = sorted_clusters[:c.charger_num]
                    c.charger_locs = [tuple(cluster['centroid']) for cluster in largest_clusters]
                    final.append(c)
                
        # Prepare final list of charger locations
        finals = []
        for place in final:
            for point in place.charger_locs:
                finals.append((point[0], point[1]))
        
        return finals    

    @staticmethod
    def adjust_chargers(coords: list, stations: list) -> list:
        """
        Adjust cluster centroids to the nearest parking/fuel station.
        """
        print("Adjusting points...")
        adjusted_clusters = []
        for centroid in coords:
            centroid_dict = {'latitude': centroid[0], 'longitude': centroid[1]}
            nearest_point = stations[0]
            nearest_point_coord = (nearest_point['latitude'], nearest_point['longitude'])
            min_distance = PointCluster.haversine_distance(
                (centroid_dict['latitude'], centroid_dict['longitude']),
                nearest_point_coord
            )
            
            for point in stations:
                point_coord = (point['latitude'], point['longitude'])
                distance = PointCluster.haversine_distance(
                    (centroid_dict['latitude'], centroid_dict['longitude']),
                    point_coord
                )
                if distance < min_distance:
                    nearest_point = point
                    min_distance = distance
            adjusted_clusters.append(nearest_point)
        return adjusted_clusters

    def find_nearest_point(self, centroid: dict, points: list) -> dict:
        """
        Find the nearest point to the given centroid from a list of points.
        """
        centroid_coord = (centroid['latitude'], centroid['longitude'])
        nearest_point = points[0]
        nearest_point_coord = (nearest_point['latitude'], nearest_point['longitude'])
        min_distance = PointCluster.haversine_distance(centroid_coord, nearest_point_coord)
        
        for point in points:
            point_coord = (point['latitude'], point['longitude'])
            distance = PointCluster.haversine_distance(centroid_coord, point_coord)
            if distance < min_distance:
                nearest_point = point
                min_distance = distance
        return nearest_point


    def point_cluster(self):
        """
        Perform DBSCAN clustering on the points and calculate cluster centroids.
        """
        if not isinstance(self.coords, np.ndarray):
            self.coords = np.array([[poi['latitude'], poi['longitude']] for poi in self.points])

        kms_per_radian = 6371.0088
        epsilon = 30000 / kms_per_radian  # 30000 meters in radians

        print("Starting point clustering...")
        db = DBSCAN(eps=epsilon, min_samples=3, metric=PointCluster.haversine_distance).fit(self.coords)

        self.labels = db.labels_

        print("Calculating points per cluster...")
        self.unique_labels = set(self.labels)
        self.clusters = {}
        for k in self.unique_labels:
            if k == -1:
                continue  # Skip noise points
            class_member_mask = (self.labels == k)
            cluster_coords = self.coords[class_member_mask]
            centroid = cluster_coords.mean(axis=0)
            self.clusters[k] = {
                'size': len(cluster_coords),
                'centroid': centroid,
                'points': cluster_coords
            }
        print(f'Number of clusters found: {len(self.clusters)}')

    def adjust_points(self, coords: list, pois: list) -> list:
        """
        Adjust cluster centroids to the nearest parking/fuel station and update POIs.
        """
        print("Adjusting points...")
        adjusted_clusters = {}
        for k, cluster_info in self.clusters.items():
            centroid = cluster_info['centroid']
            centroid_dict = {'latitude': centroid[0], 'longitude': centroid[1]}
            nearest_parking_fuel = self.find_nearest_point(centroid_dict, coords)
            adjusted_clusters[k] = {
                'size': cluster_info['size'],
                'centroid': nearest_parking_fuel,
                'points': cluster_info['points']
            }
        
        poi_list = []
        self.clusters = adjusted_clusters
        for cluster_info in self.clusters.values():
            centroid = cluster_info['centroid']
            lat = centroid["latitude"]
            lon = centroid["longitude"]
            poi = Poi.find_poi(pois, lat, lon)
            if isinstance(poi, Poi):
                lat_lon = LatLon(lat, lon)
                for thing in coords:
                    if thing['latitude'] == lat and thing['longitude'] == lon:
                        lat_lon.weight = thing['weight']
                poi = Poi(poi.getName(), poi.getType(), lat_lon)     
                poi_list.append(poi)

        lat_lons = []
        for poi in poi_list:
            coord_dict = {}
            coord_dict["latitude"] = poi.getPoint().getLat()
            coord_dict["longitude"] = poi.getPoint().getLon()
            coord_dict["weight"] = poi.getPoint().getWeight()
            lat_lons.append(coord_dict)
        return lat_lons

    def print_locations(self, pois : list):
        """
        Print the centroid coordinates of the POIs.
        """
        print("Centroid coordinates:")
        for poi in pois:
            print(poi)

    def plot(self):
        """
        Plot the clusters and their centroids.
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot original points
        ax.scatter(self.coords[:, 1], self.coords[:, 0], c='grey', alpha=0.5, label='POIs')

        print("Rendering plot...")

        # Plot clusters and centroids
        colors = plt.cm.Spectral(np.linspace(0, 1, len(self.unique_labels)))
        for k, col in zip(self.unique_labels, colors):
            if k == -1:
                continue  # Skip noise points
            class_member_mask = (self.labels == k)
            xy = self.coords[class_member_mask]

            # Plot the cluster points
            ax.scatter(xy[:, 1], xy[:, 0], c=[col], label=f'Cluster {k} Points')

            # Plot the centroid
            centroid = self.clusters[k]['centroid']
            ax.plot(centroid["longitude"], centroid["latitude"], 'o', markerfacecolor='green', markeredgecolor='green',
                    markersize=15, label=f'Centroid {k}')

        ax.set_title('DBSCAN Clustering of POIs')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()