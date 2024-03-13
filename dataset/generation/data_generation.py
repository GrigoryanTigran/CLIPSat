#!/usr/bin/env python3

from text_generation import text_gen_v1, text_gen_v2, text_gen_v3, text_gen_v4
from utils import get_image_data, split_list, get_image_paths

from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import pandas as pd
import argparse
import random
import os

def generate_from_image_paths(image_paths, text_generator):
    laion_data = pd.DataFrame(columns = ["FilePath", "Text", "License Information", "Image Hash", "GSD", "Metadata Path", "OSM Data Path", "UTM", "Country Code", "Timestamp"])

    for image_path in image_paths:
        json_path = image_path[:-3] + "json"
        osm_path = image_path[:-3] + "csv"
        if not (os.path.exists(json_path) and os.path.exists(osm_path)):
            continue
        # Generate text for the image
        metadata = get_image_data(image_path)["metadata"]
        osm_raw_data = pd.read_csv(osm_path, sep=';')

        generated_text = text_generator(osm_raw_data)
        if generated_text == "":
            continue
        laion_data.loc[len(laion_data.index)] = [image_path, generated_text, "Unknown", "N/A", metadata["gsd"], 
                                                 json_path, osm_path, metadata["utm"], metadata["country_code"], metadata["timestamp"]]
    

    return laion_data

def main(args):
    generators = {"v1": text_gen_v1,
                  "v2": text_gen_v2,
                  "v3": text_gen_v3,
                  "v4": text_gen_v4,
                  }

    os.makedirs(args.output_laion_dir, exist_ok=True)
    image_paths = get_image_paths(args.fmow_dataset)
    random.shuffle(image_paths)
    splited_image_paths = split_list(image_paths, args.workers)
    
    data_frames = {}
    version = args.text_generator_version
    with ProcessPoolExecutor() as executor:
        print("Generating data with version", version)
        data_frames = list(executor.map(generate_from_image_paths, splited_image_paths, [generators[version]]*args.workers))

        if not len(data_frames):
            print("Cannot generate data with version", version)
            return
        full_laion_data = pd.concat(data_frames, ignore_index=True)

        if len(full_laion_data):
            data_path = os.path.join(args.output_laion_dir, f"laion_sat_{version}_dataset.csv")
            full_laion_data.to_csv(data_path, index=False, sep=";")


if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description="Generate LAION dataset from Enriched and cropped fmow dataset.")
    parser.add_argument('-d', "--fmow-dataset", type=str, required=True, help="FMoW dataset Directory.")
    parser.add_argument('-out', '--output-laion-dir', type=str, required=True, help="LAION dataset directory.")
    parser.add_argument('-t', '--text-generator-version', type=str, required=True, help="Text generation versions.")
    parser.add_argument('-w', '--workers', type=int, default=8, help="Number of Parallel workers.")

    
    args = parser.parse_args()
    main(args)
