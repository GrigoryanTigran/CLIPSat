from osm_data_processing import extract_OSM_data

from shapely.geometry import Polygon, Point, MultiPolygon
from shapely import wkt, covered_by
import geopandas as gpd
import itertools
import math
import random
import pandas as pd
import time

def text_gen_v1(data):
    text = "There are"
    num = 0 if "aeroway" not in data else data[data['aeroway'].notnull()].shape[0]
    text += f" {num} aeroways," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "natural" not in data else data[data['natural'].notnull()].shape[0]
    text += f" {num} natural zones," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "man_made" not in data else data[data['man_made'].notnull()].shape[0]
    text += f" {num} man made areas," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "railway" not in data else data[data['railway'].notnull()].shape[0]
    text += f" {num} railways," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "waterway" not in data else data[data['waterway'].notnull()].shape[0]
    text += f" {num} waterways," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "highway" not in data else data[data['highway'].notnull()].shape[0]
    text += f" {num} highways," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","

    num = 0 if "building" not in data else data[data['building'].notnull()].shape[0]
    text += f" {num} buildings," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","
    
    num = 0 if "amenity" not in data else data[data['amenity'].notnull()].shape[0]
    text += f" {num} amenities," if num != 0 else ""
    if num == 1:
        text = text[:-4] + "y,"
    
    num = 0 if "landuse" not in data else data[data['landuse'].notnull()].shape[0]
    text += f" {num} landuse zones," if num != 0 else ""
    if num == 1:
        text = text[:-2] + ","

    if text == "There are":
        return ""
    return text.strip(',')

def text_gen_v2(data):
    return ""
    
def text_gen_v3(raw_data):
    text = ""
    data = extract_OSM_data(raw_data)
    for i, (key1, poly1) in enumerate(data.items()):
        for j, (key2, poly2) in enumerate(data.items()):
            if j < i:
                continue
            obj1 = key1.rsplit('-', 1)[0].replace('_', " ")
            obj2 = key2.rsplit('-', 1)[0].replace('_', " ")
            if obj1 == obj2:
                continue
            if are_polygons_near(poly1, poly2):
                if covered_by(poly1, poly2):
                    text_part = f"{obj1} is covered by {obj2}. "
                elif covered_by(poly2, poly1):
                    text_part = f"{obj1} coveres {obj2}. "
                else:
                    centroid1 = calculate_centroid(poly1)  # Returns (longitude, latitude)
                    centroid2 = calculate_centroid(poly2)  # Returns (longitude, latitude)

                    bearing = calculate_bearing(centroid1, centroid2)
                    cardinal_direction = bearing_to_cardinal(bearing)

                    text_part = f"{obj2} is {cardinal_direction} of {obj1}. "
                if text_part not in text:
                    text += text_part
    return text.strip()

def text_gen_v4(data):
    return ""

def are_polygons_near(poly1, poly2, threshold=500):
    """Check if two polygons are within a specified distance in meters."""
    # Convert polygons to GeoSeries to use the buffer method
    gpd_poly1 = gpd.GeoSeries([poly1])
    gpd_poly2 = gpd.GeoSeries([poly2])
    
    # Use buffer to create a zone around poly1 with the given threshold, and check if poly2 intersects this zone
    buffered_zone = gpd_poly1.buffer(threshold / 100000)  # Rough conversion for degrees to meters
    return buffered_zone.intersects(poly2).any()


def calculate_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    
    The formulae used is:
    θ = atan2(sin(Δlong).cos(lat2),
              cos(lat1).sin(lat2) - sin(lat1).cos(lat2).cos(Δlong))
    
    :param pointA: tuple containing the latitude/longitude for the first point
    :param pointB: tuple containing the latitude/longitude for the second point
    :returns: bearing in degrees
    """
    lat1, lon1 = math.radians(pointA[1]), math.radians(pointA[0])
    lat2, lon2 = math.radians(pointB[1]), math.radians(pointB[0])
    
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dLon))
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360  # Normalize to 0-360
    
    return bearing

def bearing_to_cardinal(bearing):
    """
    Converts a bearing to a cardinal direction.
    """
    if random.randint(0, 1):
        cardinals = ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west', 'north']
    else:
        cardinals = ['above', "above-right", "right", "below-right", "below", "below-left", "left", "above-left", "above"]
    return cardinals[int(round(bearing / 45)) % 8]

def calculate_centroid(polygon):
    return polygon.centroid.x, polygon.centroid.y


