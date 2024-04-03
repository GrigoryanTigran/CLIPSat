# LAION-like Dataset Generation from FMoW Dataset

This sub-project is focused on generating a LAION-like dataset utilizing the images from the Functional Map of the World (FMoW) dataset. The process enriches FMoW dataset images with OpenStreetMaps data, crops the satellite images to manageable sizes, and generates descriptive texts for each image. The generated dataset aims to be a valuable resource for machine learning models, specifically those requiring detailed geographic and contextual data.

## Overview

The project consists of three main steps:

1. **Metadata Enrichment**: Enriching the FMoW dataset's image metadata with OpenStreetMaps data.
2. **Image Cropping**: Cropping large satellite images into smaller, manageable tiles along with their corresponding metadata.
3. **Text Generation**: Generating descriptive texts for each image to accompany the visual data.

## Usage

### 1. Metadata Enrichment

Run the `enrich_with_osm.py` script to enrich the FMoW dataset's image metadata with OpenStreetMaps data.
```bash
python enrich_with_osm.py --fmow-dataset <FMoW dataset directory> --output-dir <output directory> --workers <number of threads>
```
Arguments:
- `-d, --fmow-dataset`: Directory of the FMoW dataset.
- `-out, --output-dir`: Directory where the enriched dataset will be saved.
- `-w, --workers`: Number of parallel threads (default is 4).

### 2. Image Cropping

After enrichment, use the `tile_dataset.py` script to crop the satellite images into smaller tiles. This script also crops corresponding metadata and OSM data.
```bash
python tile_dataset.py --fmow-e-dataset <FMoW enriched dataset directory> --output-dir <output directory> --tile-size <tile size> --overlap <overlap between tiles> --workers <number of threads>
```

Arguments:
- `-d, --fmow-e-dataset`: Directory of the enriched FMoW dataset.
- `-out, --output-dir`: Directory where the cropped images will be saved.
- `-ts, --tile-size`: Size of the cropping tile (default is 512 pixels).
- `-ol, --overlap`: Overlap between tiles in pixels (default is 32).
- `-w, --workers`: Number of parallel threads (default is 4).

### 3. Text Generation

Finally, run the text generation script to generate descriptive texts for each image. This script supports four versions of text generators.
```bash
python text_generation.py --fmow-dataset <cropped FMoW dataset directory> --output-laion-dir <LAION dataset directory> --text-generator-version <v1/v2/v3/v4> --workers <number of threads>
```

Arguments:
- `-d, --fmow-dataset`: Directory of the cropped FMoW dataset.
- `-out, --output-laion-dir`: Directory where the LAION dataset will be saved.
- `-t, --text-generator-version`: Version of the text generation algorithm to use (`v1`, `v2`, `v3`, `v4`).
- `-w, --workers`: Number of parallel workers (default is 8).

## Text Generator Versions

- **V1**: Generates a basic count of natural zones, waterways, highways, etc.
- **V2**: Enumerates all objects, separated by commas.
- **V3**: Provides detailed descriptions including the direction of objects from one another, using geographical directions or covering relationships.
- **V4**: Enhances V3's output by translating it into a more natural English representation using the T5 transformer model.



# LAION-Sat Dataset Visualizer

The LAION-Sat Dataset Visualizer is a web application designed to enable users to easily visualize and interact with the LAION dataset in CSV format. Utilizing a map interface, users can upload LAION CSV data and visually explore each row based on text, with additional functionality for viewing truncated text in full.

## Features

- **Upload LAION Dataset**: Users can upload a LAION dataset in CSV format for visualization.
- **Interactive Map Interface**: Powered by ArcGIS, the map allows for visual exploration of the dataset.
- **Clickable Table Rows**: Display data points on the map by clicking on corresponding fields in the table.
- **Expandable Text**: Clickable text in the table cells allows users to view the full text for truncated data.
- **Toggle Table Visibility**: Manage screen space by toggling the visibility of the dataset table.

## Running the Application

Execute the following command to start the web server:
```bash
python3 app.py
```
Then, open a web browser and go to `127.0.0.1:5000` to access the visualizer.

## Usage

- **Uploading Data**: Click the "Choose File" button to upload your LAION CSV dataset, then click "Submit".
- **Viewing Data on Map**: Click on a row in the table to visualize the corresponding data point on the map.
- **Expanding Truncated Text**: Click on the `...` in any table cell to view the full text.
- **Toggle Table Visibility**: Use the toggle button below the table to hide/show the table for better map visibility.
