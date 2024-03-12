#!/usr/bin/env python3
from utils import *

from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import osmnx as ox
import argparse
import os

def get_osm_data(polygon):
    highway_interest = ["trunk", "primary", "secondary", "tertiary", "unclassified",
                        "trunk_link", "primary_link", "secondary_link", "tertiary_link"]
    try:
        features = ox.features_from_polygon(polygon, tags={"building": True, "highway": highway_interest, "landuse": True,
                                                                            "natural": True, "man_made": True, "amenity": True,
                                                                            "aeroway": True, "railway": True,  "waterway":True})
    
        features = features[features.geom_type.isin(['Polygon', 'MultiPolygon', "LineString"])]
        return features
    except:
        return pd.DataFrame()

def enrich_images(image_paths, output_dir):
    for img_path in image_paths:
        features = get_osm_data(get_polygon_from_image_path(img_path))
        _, class_name, instance_id, image_name = img_path.rsplit("/")
        new_img_path = os.path.join(output_dir, class_name, instance_id, image_name)

        metadata_path = img_path.replace("_rgb.jpg", "_rgb.json")
        new_metadata_path = new_img_path.replace("_rgb.jpg", "_rgb.json")

        osm_data_path = new_img_path.replace("_rgb.jpg", "_rgb.csv")
        
        os.makedirs(os.path.dirname(osm_data_path), exist_ok=True)
        features.to_csv(osm_data_path, index=False, sep=';')
        os.symlink(os.path.join(os.getcwd(), img_path), new_img_path)
        os.symlink(os.path.join(os.getcwd(), metadata_path), new_metadata_path)
        
    return

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process FMoW dataset.")
    parser.add_argument('-d', "--fmow-dataset", type=str, help="FMoW dataset Directory")
    parser.add_argument('-out', "--output-dir", type=str, help="Output Directory")
    parser.add_argument('-w', '--workers', type=int, default=4, help="Number of parallel threads")

    args = parser.parse_args()

    image_paths = get_newest_image_paths(args.fmow_dataset)

    os.makedirs(args.output_dir, exist_ok=True)

    splited_image_paths = list(split_list(image_paths, args.workers))
    
    with ThreadPoolExecutor() as executor:
        executor.map(enrich_images, splited_image_paths, [args.output_dir] * args.workers)
