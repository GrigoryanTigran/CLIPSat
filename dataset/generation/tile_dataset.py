#!/usr/bin/env python3

from preprocess_fmow import PreProcessFMoW

import argparse

def main(args):
    preprocesser = PreProcessFMoW(args.fmow_e_dataset, args.output_dir, args.tile_size, args.overlap, args.workers)
    preprocesser()


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process FMoW dataset.")
    parser.add_argument('-d', "--fmow-e-dataset", type=str, help="FMoW dataset *Enriched with OSM* Directory")
    parser.add_argument('-out', "--output-dir", type=str, help="Output Directory")
    parser.add_argument('-ts', '--tile-size', type=int, default=512, help="Cropping Tile size")
    parser.add_argument('-ol', '--overlap', type=int, default=32, help="Overlap between tiles")
    parser.add_argument('-w', '--workers', type=int, default=4, help="Number of parallel threads")

    args = parser.parse_args()
    main(args)
