#!/usr/bin/env python
"""
Batch-process a directory of EM volumes through the NeuronSegmenter pipeline.

Author: Kevin Druciak (kevintdruciak@gmail.com)

Usage (run inside 3D Slicer's Python environment):

    Slicer --python-script batch_segment_em.py \
        --input-dir /path/to/em_stacks \
        --output-dir /path/to/output \
        --sigma 1.0 \
        --threshold 128 \
        --min-size 500

Supported input formats: .nrrd, .nii, .nii.gz, .tiff, .tif
Output: one NRRD label map per input volume.
"""

import argparse
import glob
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".nrrd", ".nii", ".nii.gz", ".tiff", ".tif")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch neuron segmentation of EM volumes in 3D Slicer."
    )
    parser.add_argument(
        "--input-dir", required=True, help="Directory containing EM volume files."
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory to write label map outputs."
    )
    parser.add_argument(
        "--sigma", type=float, default=1.0,
        help="Gaussian smoothing sigma (default: 1.0).",
    )
    parser.add_argument(
        "--threshold", type=int, default=128,
        help="Membrane intensity threshold 0-255 (default: 128).",
    )
    parser.add_argument(
        "--min-size", type=int, default=500,
        help="Minimum segment size in voxels (default: 500).",
    )
    return parser.parse_args()


def find_volumes(input_dir):
    """Return sorted list of volume file paths with supported extensions."""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(glob.glob(os.path.join(input_dir, f"*{ext}")))
    files.sort()
    return files


def process_volume(filepath, output_dir, sigma, threshold, min_size):
    """Load a single volume, segment it, and save the label map."""
    import slicer

    basename = os.path.splitext(os.path.basename(filepath))[0]
    if basename.endswith(".nii"):
        basename = basename[:-4]

    logger.info(f"Loading: {filepath}")
    volume_node = slicer.util.loadVolume(filepath)

    seg_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentationNode", f"{basename}_segmentation"
    )

    logic_module = slicer.modules.neuronsegmenter.widgetRepresentation().self().logic
    params = {
        "gaussian_sigma": sigma,
        "membrane_threshold": threshold,
        "min_segment_size": min_size,
        "fill_holes": True,
    }
    logic_module.run_segmentation(volume_node, seg_node, params)

    labelmap_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLLabelMapVolumeNode", f"{basename}_labels"
    )
    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(
        seg_node, labelmap_node, slicer.vtkSegmentation.EXTENT_REFERENCE_GEOMETRY
    )

    output_path = os.path.join(output_dir, f"{basename}_labels.nrrd")
    slicer.util.saveNode(labelmap_node, output_path)
    logger.info(f"Saved: {output_path}")

    slicer.mrmlScene.RemoveNode(volume_node)
    slicer.mrmlScene.RemoveNode(seg_node)
    slicer.mrmlScene.RemoveNode(labelmap_node)


def main():
    args = parse_args()

    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    volumes = find_volumes(args.input_dir)
    if not volumes:
        logger.warning(f"No supported volumes found in {args.input_dir}")
        sys.exit(0)

    logger.info(f"Found {len(volumes)} volume(s) to process")

    for i, filepath in enumerate(volumes, start=1):
        logger.info(f"[{i}/{len(volumes)}] Processing {os.path.basename(filepath)}")
        try:
            process_volume(
                filepath, args.output_dir,
                args.sigma, args.threshold, args.min_size,
            )
        except Exception as e:
            logger.error(f"Failed on {filepath}: {e}", exc_info=True)

    logger.info("Batch segmentation complete")


if __name__ == "__main__":
    main()
