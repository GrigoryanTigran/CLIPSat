#!/bin/bash

fmow=$1
workers=$2

echo "Enriching fmow data with OSM"
./enrich_with_osm.py -d $fmow -out "processed_fmow/enriched" -w $workers
echo "Done in 'processed_fmow/enriched'"

echo "Cropping into Tiles"
./tile_dataset.py -d "processed_fmow/enriched" -out "processed_fmow/cropped" -ts 512 -ol 16 -w $workers
echo "Done in 'processed_fmow/cropped'"

echo "Generating LAION Dataset with v1 text generator"
./data_generation.py -d "processed_fmow/cropped" -out "processed_fmow" -t v1 -w $workers

echo "Generating LAION Dataset with v3 text generator"
./data_generation.py -d "processed_fmow/cropped" -out "processed_fmow" -t v3 -w $workers

echo "Done in 'processed_fmow'"
