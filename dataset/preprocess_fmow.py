from utils import *

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from shapely.geometry import Polygon
from shapely import wkt
import pandas as pd
import math
import json
import os

class PreProcessFMoW:
    def __init__(self, fmow_dataset, output_dir, tile_size=512, overlap=32, workers=4):
        self.fmow_dataset = fmow_dataset
        self.output_dir = output_dir
        self.tile_size = tile_size
        self.overlap = overlap
        self.num_processes = int(math.sqrt(workers))
        self.num_threads_in_process = self.num_processes - 1
        os.makedirs(self.output_dir, exist_ok=True)

    def __call__(self):
        image_paths = get_image_paths(self.fmow_dataset)
        splited_image_paths = list(split_list(image_paths, self.num_processes))
        with ProcessPoolExecutor() as process_executor:
            process_executor.map(self.preprocess_list_of_images, splited_image_paths)
    
    def preprocess_list_of_images(self, image_paths):
        for img_path in image_paths:
            image_data = get_metadata(img_path)
            self.preprocess_image(image_data)
         
    def preprocess_image(self, image_data):
        image = image_data["image"]
        metadata = image_data["metadata"]
        image_path = image_data["image_path"]
        full_image_path = os.path.join(image_data["image_basedir"], image_path)
        osm_data_path = full_image_path.replace(".jpg", ".csv")
        try:
            osm_data = pd.read_csv(osm_data_path, sep=";", low_memory=False)
        except:
            return
        osm_data["geometry"] = osm_data["geometry"].astype(str).apply(wkt.loads)
        width, height, _ = image.shape
        tiles = self.generate_tiles(width, height)
        splited_tiles = split_list(tiles, self.num_threads_in_process)
        tile_image_dir = os.path.join(self.output_dir, os.path.dirname(image_path))
        os.makedirs(tile_image_dir, exist_ok=True)

        def process_tiles(tiles):
            for i, tile_box in enumerate(tiles):
                img_tile = image[tile_box[0]:tile_box[2], tile_box[1]:tile_box[3]]
                tile_filename = f'{os.path.basename(image_path).rsplit(".", 1)[0]}_tile_{i}.jpg'
                tile_image_path = os.path.join(tile_image_dir, tile_filename)
                tile_metadata_path = tile_image_path.replace(".jpg", ".json")
                tile_osm_path = tile_image_path.replace(".jpg", ".csv")

                cv2.imwrite(tile_image_path, img_tile)

                # Update JSON
                tile_metadata = self.update_metadata_for_tile(metadata, tile_box)
                tile_metadata["original_image_path"] = full_image_path 

                # Save updated JSON for the tile
                with open(tile_metadata_path, 'w') as f_out:
                    json.dump(tile_metadata, f_out, indent=4)

                # Update OSM Data
                image_polygon = wkt.loads(tile_metadata["raw_location"])
                tile_osm = osm_data.copy()
                tile_osm = tile_osm[tile_osm['geometry'].apply(lambda geom: geom.intersects(image_polygon))]
                tile_osm['geometry'] = tile_osm['geometry'].apply(lambda geom: geom.intersection(image_polygon))

                # Save Updates OSM Data
                tile_osm.to_csv(tile_osm_path, sep=";", index=False)
            return

        with ThreadPoolExecutor() as thread_executor:
            thread_executor.map(process_tiles, splited_tiles)

    
    def generate_tiles(self, width, height):
        """
        Generate tile coordinates with overlap.
        Returns a list of tuples (left, upper, right, lower) for each tile.
        """
        tiles = []
        step_size = self.tile_size - self.overlap
        for y in range(0, height, step_size):
            for x in range(0, width, step_size):
                left = x
                upper = y
                right = min(x + self.tile_size, width)
                lower = min(y + self.tile_size, height)
                if right - left < self.tile_size:
                    left = max(0, right - self.tile_size)
                if lower - upper < self.tile_size:
                    upper = max(0, lower - self.tile_size)
                tiles.append((left, upper, right, lower))
        return tiles

    def update_metadata_for_tile(self, metadata, tile_box):
        """
        Update metadata for a specific tile.
        Adjusts bounding boxes and other relevant information for the cropped area.
        """
        new_metadata = metadata.copy()  # Deep copy might be necessary depending on the structure
        new_metadata['bounding_boxes'] = []  # Reset bounding boxes for this tile
        new_metadata["img_width"] = tile_box[2] - tile_box[0]
        new_metadata["img_height"] = tile_box[3] - tile_box[1]
        big_polygon = wkt.loads(metadata["raw_location"])
        lng_step = (big_polygon.exterior.coords[1][0] - big_polygon.exterior.coords[0][0]) / metadata["img_width"]
        lat_step = (big_polygon.exterior.coords[2][1] - big_polygon.exterior.coords[1][1]) / metadata["img_height"]
        top_lat, left_lng = big_polygon.exterior.coords[3]
        top_left = (top_lat + lat_step * tile_box[0], left_lng - lng_step * tile_box[1])
        lower_right = (top_lat + lat_step * tile_box[2], left_lng - lng_step * tile_box[3])
        new_metadata['raw_location'] = self.create_bounding_box(top_left, lower_right).wkt
        return new_metadata

    def create_bounding_box(self, point1, point2):
        """
        Create a bounding box polygon from two points.

        Parameters:
        - point1: The first point as a tuple (x, y)
        - point2: The second point as a tuple (x, y)

        Returns:
        - A Shapely Polygon representing the bounding box.
        """
        # Calculate min and max coordinates to ensure correct bounding box
        min_x = min(point1[0], point2[0])
        max_x = max(point1[0], point2[0])
        min_y = min(point1[1], point2[1])
        max_y = max(point1[1], point2[1])

        # Define the coordinates of the bounding box's corners
        bottom_left = (min_x, min_y)
        bottom_right = (max_x, min_y)
        top_right = (max_x, max_y)
        top_left = (min_x, max_y)

        # Create the bounding box as a polygon
        bounding_box = Polygon([bottom_left, bottom_right, top_right, top_left, bottom_left])

        return bounding_box

