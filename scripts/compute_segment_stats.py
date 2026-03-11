#!/usr/bin/env python
"""
Compute per-neuron morphological statistics from a segmentation.

Author: Kevin Druciak (kevintdruciak@gmail.com)

Usage (run inside 3D Slicer's Python environment):

    Slicer --python-script compute_segment_stats.py \
        --segmentation /path/to/labels.nrrd \
        --reference-volume /path/to/em_volume.nrrd \
        --output-csv /path/to/stats.csv

Metrics computed per segment:
  - Volume (mm^3)
  - Surface area (mm^2)
  - Centroid (RAS coordinates)
  - Bounding box dimensions
  - Voxel count
"""

import argparse
import csv
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute per-neuron statistics from a label map."
    )
    parser.add_argument(
        "--segmentation", required=True,
        help="Path to the label map volume.",
    )
    parser.add_argument(
        "--reference-volume", required=True,
        help="Path to the reference EM volume (for geometry).",
    )
    parser.add_argument(
        "--output-csv", required=True,
        help="Path to write the output CSV file.",
    )
    return parser.parse_args()


def compute_stats_slicer(segmentation_path, reference_path, output_csv):
    """Use Slicer's SegmentStatistics module to compute metrics."""
    import slicer

    logger.info(f"Loading reference volume: {reference_path}")
    volume_node = slicer.util.loadVolume(reference_path)

    logger.info(f"Loading segmentation: {segmentation_path}")
    labelmap_node = slicer.util.loadLabelVolume(segmentation_path)

    seg_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentationNode", "StatsSegmentation"
    )
    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
        labelmap_node, seg_node
    )

    import SegmentStatistics
    stats_logic = SegmentStatistics.SegmentStatisticsLogic()
    stats_logic.getParameterNode().SetParameter("Segmentation", seg_node.GetID())
    stats_logic.getParameterNode().SetParameter(
        "ScalarVolume", volume_node.GetID()
    )
    stats_logic.computeStatistics()

    results = stats_logic.getStatistics()

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)

    segment_ids = seg_node.GetSegmentation().GetSegmentIDs()
    fieldnames = [
        "segment_id", "segment_name", "voxel_count",
        "volume_mm3", "surface_area_mm2",
        "centroid_ras_x", "centroid_ras_y", "centroid_ras_z",
    ]

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for seg_id in segment_ids:
            segment = seg_node.GetSegmentation().GetSegment(seg_id)
            stats = results.get(seg_id, {})

            centroid = stats.get(
                "LabelmapSegmentStatisticsPlugin.centroid_ras", [0, 0, 0]
            )

            row = {
                "segment_id": seg_id,
                "segment_name": segment.GetName() if segment else seg_id,
                "voxel_count": stats.get(
                    "LabelmapSegmentStatisticsPlugin.voxel_count", 0
                ),
                "volume_mm3": stats.get(
                    "LabelmapSegmentStatisticsPlugin.volume_mm3", 0
                ),
                "surface_area_mm2": stats.get(
                    "ClosedSurfaceSegmentStatisticsPlugin.surface_area_mm2", 0
                ),
                "centroid_ras_x": centroid[0] if len(centroid) > 0 else 0,
                "centroid_ras_y": centroid[1] if len(centroid) > 1 else 0,
                "centroid_ras_z": centroid[2] if len(centroid) > 2 else 0,
            }
            writer.writerow(row)

    logger.info(f"Wrote statistics for {len(list(segment_ids))} segments to {output_csv}")

    slicer.mrmlScene.RemoveNode(volume_node)
    slicer.mrmlScene.RemoveNode(labelmap_node)
    slicer.mrmlScene.RemoveNode(seg_node)


def main():
    args = parse_args()
    compute_stats_slicer(args.segmentation, args.reference_volume, args.output_csv)


if __name__ == "__main__":
    main()
