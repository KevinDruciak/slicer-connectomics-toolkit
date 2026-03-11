#!/usr/bin/env python
"""
Export segmented neurons as individual 3D surface meshes (STL or OBJ).

Author: Kevin Druciak (kevintdruciak@gmail.com)

Usage (run inside 3D Slicer's Python environment):

    Slicer --python-script export_neuron_meshes.py \
        --segmentation /path/to/labels.nrrd \
        --output-dir /path/to/meshes \
        --format stl

Each labeled neuron is extracted via VTK marching cubes, smoothed, and
written as a separate mesh file named neuron_<ID>.<format>.
"""

import argparse
import logging
import os
import sys

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export neuron segments as 3D surface meshes."
    )
    parser.add_argument(
        "--segmentation", required=True,
        help="Path to a label map volume (NRRD, NIfTI).",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory to write mesh files.",
    )
    parser.add_argument(
        "--format", choices=["stl", "obj"], default="stl",
        help="Output mesh format (default: stl).",
    )
    parser.add_argument(
        "--smoothing-iterations", type=int, default=25,
        help="Number of Laplacian smoothing iterations (default: 25).",
    )
    return parser.parse_args()


def extract_and_export(label_array, spacing, origin, label_id, output_path,
                       smoothing_iterations):
    """Extract a surface mesh for a single label and write it to disk."""
    import vtk

    binary = np.zeros_like(label_array, dtype=np.uint8)
    binary[label_array == label_id] = 1

    vtk_data = vtk.vtkImageData()
    vtk_data.SetDimensions(binary.shape[2], binary.shape[1], binary.shape[0])
    vtk_data.SetSpacing(spacing)
    vtk_data.SetOrigin(origin)
    vtk_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    flat = binary.flatten(order="C")
    for i in range(len(flat)):
        vtk_data.GetPointData().GetScalars().SetValue(i, int(flat[i]))

    marching = vtk.vtkMarchingCubes()
    marching.SetInputData(vtk_data)
    marching.SetValue(0, 0.5)
    marching.Update()

    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputConnection(marching.GetOutputPort())
    smoother.SetNumberOfIterations(smoothing_iterations)
    smoother.SetRelaxationFactor(0.1)
    smoother.FeatureEdgeSmoothingOff()
    smoother.BoundarySmoothingOn()
    smoother.Update()

    if output_path.endswith(".stl"):
        writer = vtk.vtkSTLWriter()
    else:
        writer = vtk.vtkOBJWriter()

    writer.SetFileName(output_path)
    writer.SetInputConnection(smoother.GetOutputPort())
    writer.Write()


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    try:
        import nrrd
        label_array, header = nrrd.read(args.segmentation)
        spacing = header.get("space directions", np.eye(3))
        spacing = tuple(np.abs(np.diag(spacing[:3, :3])))
        origin = tuple(header.get("space origin", (0.0, 0.0, 0.0)))
    except ImportError:
        import nibabel as nib
        img = nib.load(args.segmentation)
        label_array = np.asarray(img.dataobj, dtype=np.int32)
        spacing = tuple(img.header.get_zooms()[:3])
        origin = tuple(img.affine[:3, 3])

    unique_labels = np.unique(label_array)
    unique_labels = unique_labels[unique_labels != 0]
    logger.info(f"Found {len(unique_labels)} neuron segments")

    for label_id in unique_labels:
        output_path = os.path.join(
            args.output_dir, f"neuron_{label_id:04d}.{args.format}"
        )
        logger.info(f"Exporting label {label_id} -> {output_path}")
        try:
            extract_and_export(
                label_array, spacing, origin, label_id, output_path,
                args.smoothing_iterations,
            )
        except Exception as e:
            logger.error(f"Failed on label {label_id}: {e}", exc_info=True)

    logger.info(f"Exported {len(unique_labels)} meshes to {args.output_dir}")


if __name__ == "__main__":
    main()
