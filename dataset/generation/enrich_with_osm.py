#!/usr/bin/env python3
from utils import *

from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import osmnx as ox
import argparse
import tqdm
import sys
import os
import multiprocessing

def run_task_with_timeout(func, polygon, timeout):
    sys.stdout.flush()
    # Define a wrapper function to capture the task's return value and send it through a pipe
    def wrapper_func(conn):
        result = func(polygon)
        conn.send(result)
        conn.close()
    
    # Create a Pipe for communication
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # Create a Process object with the wrapper function and start it
    proc = multiprocessing.Process(target=wrapper_func, args=(child_conn,))
    proc.start()
    
    # Wait for the process to complete or timeout
    proc.join(timeout)
    
    if proc.is_alive():
        # If the process is still alive after the timeout, terminate it
        print("Terminating due to timeout of polygon", polygon)
        proc.terminate()
        proc.join()
        return pd.DataFrame()
    else:
        # If the process completed within the timeout, retrieve and return the result
        if parent_conn.poll():
            result = parent_conn.recv()
            return result
        else:
            print("Task completed but no result was returned of polygon", polygon.wkt)
            return pd.DataFrae()

def get_osm_data(polygon):
    highway_interest = ["trunk", "primary", "secondary", "tertiary", "unclassified",
                        "trunk_link", "primary_link", "secondary_link", "tertiary_link"]
    try:
        features = ox.features_from_polygon(polygon, tags={"building": True, "highway": highway_interest, "landuse": True,
                                                                            "natural": True, "man_made": True, "amenity": True,
                                                                            "aeroway": True, "railway": True,  "waterway":True})
    
        features = features[features.geom_type.isin(['Polygon', 'MultiPolygon', "LineString"])]
        return features
    except Exception as error:
        print("An exception occurred:", error, "There is no OSM data for polygon", polygon)
        sys.stdout.flush()
        return pd.DataFrame()

def enrich_images(image_paths, output_dir):
    for img_path in tqdm.tqdm(image_paths):
        _, class_name, instance_id, image_name = img_path.rsplit("/", 3)
        new_img_path = os.path.join(output_dir, class_name, instance_id, image_name)
        osm_data_path = new_img_path.replace("_rgb.jpg", "_rgb.csv")
        if os.path.exists(osm_data_path):
            continue
        features = run_task_with_timeout(get_osm_data, get_polygon_from_image_path(img_path), 120)
        if len(features) == 0:
            print("There is no osm data for ", img_path)

        metadata_path = img_path.replace("_rgb.jpg", "_rgb.json")
        new_metadata_path = new_img_path.replace("_rgb.jpg", "_rgb.json")

        
        os.makedirs(os.path.dirname(osm_data_path), exist_ok=True)
        features.to_csv(osm_data_path, index=False, sep=';')
        if not os.path.exists(new_img_path):
            os.symlink(os.path.join(os.getcwd(), img_path), new_img_path)
        if not os.path.exists(new_metadata_path):
            os.symlink(os.path.join(os.getcwd(), metadata_path), new_metadata_path)
        sys.stdout.flush()

        
    return

def main(args):
    image_paths = get_newest_image_paths(args.fmow_dataset)

    os.makedirs(args.output_dir, exist_ok=True)
    #enrich_images(image_paths, args.output_dir)
    splited_image_paths = list(split_list(image_paths, args.workers))
    
    #for _ in splited_image_paths:
    #    enrich_images(_, args.output_dir)
    with ProcessPoolExecutor() as executor:
        executor.map(enrich_images, splited_image_paths, [args.output_dir] * args.workers)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process FMoW dataset.")
    parser.add_argument('-d', "--fmow-dataset", type=str, help="FMoW dataset Directory")
    parser.add_argument('-out', "--output-dir", type=str, help="Output Directory")
    parser.add_argument('-w', '--workers', type=int, default=4, help="Number of parallel threads")

    args = parser.parse_args()
    main(args)
