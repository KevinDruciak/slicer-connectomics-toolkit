#!/usr/bin/env python
"""
Register an EM volume to a reference atlas coordinate frame.

Author: Kevin Druciak (kevintdruciak@gmail.com)

Uses 3D Slicer's BRAINSFit module for rigid and affine registration.
The output is a resampled volume aligned to the atlas and the computed
transform, which can be applied to label maps or meshes.

Usage (run inside 3D Slicer's Python environment):

    Slicer --python-script register_to_atlas.py \
        --moving /path/to/em_volume.nrrd \
        --fixed /path/to/atlas_volume.nrrd \
        --output-volume /path/to/registered.nrrd \
        --output-transform /path/to/transform.h5 \
        --registration-type affine
"""

import argparse
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
        description="Register an EM volume to a reference atlas using BRAINSFit."
    )
    parser.add_argument(
        "--moving", required=True,
        help="Path to the moving (EM) volume.",
    )
    parser.add_argument(
        "--fixed", required=True,
        help="Path to the fixed (atlas) volume.",
    )
    parser.add_argument(
        "--output-volume", required=True,
        help="Path to write the registered output volume.",
    )
    parser.add_argument(
        "--output-transform", default=None,
        help="Path to write the computed transform (HDF5 or .tfm).",
    )
    parser.add_argument(
        "--registration-type",
        choices=["rigid", "affine", "bspline"],
        default="affine",
        help="Type of registration (default: affine).",
    )
    parser.add_argument(
        "--sampling-percentage", type=float, default=0.05,
        help="Fraction of voxels to sample for metric evaluation (default: 0.05).",
    )
    return parser.parse_args()


def run_registration(args):
    """Execute BRAINSFit registration within 3D Slicer."""
    import slicer

    logger.info(f"Loading fixed volume: {args.fixed}")
    fixed_node = slicer.util.loadVolume(args.fixed)

    logger.info(f"Loading moving volume: {args.moving}")
    moving_node = slicer.util.loadVolume(args.moving)

    output_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLScalarVolumeNode", "RegisteredVolume"
    )
    transform_node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLLinearTransformNode", "RegistrationTransform"
    )

    params = {
        "fixedVolume": fixed_node.GetID(),
        "movingVolume": moving_node.GetID(),
        "outputVolume": output_node.GetID(),
        "linearTransform": transform_node.GetID(),
        "useRigid": args.registration_type == "rigid",
        "useAffine": args.registration_type == "affine",
        "useBSpline": args.registration_type == "bspline",
        "samplingPercentage": args.sampling_percentage,
        "initializeTransformMode": "useCenterOfHeadAlign",
        "interpolationMode": "Linear",
    }

    logger.info(f"Running BRAINSFit ({args.registration_type} registration)")
    cli_node = slicer.cli.runSync(slicer.modules.brainsfit, None, params)

    if cli_node.GetStatus() & cli_node.ErrorsMask:
        error_text = cli_node.GetErrorText()
        raise RuntimeError(f"BRAINSFit failed: {error_text}")

    os.makedirs(os.path.dirname(os.path.abspath(args.output_volume)), exist_ok=True)
    slicer.util.saveNode(output_node, args.output_volume)
    logger.info(f"Saved registered volume: {args.output_volume}")

    if args.output_transform:
        os.makedirs(
            os.path.dirname(os.path.abspath(args.output_transform)), exist_ok=True
        )
        slicer.util.saveNode(transform_node, args.output_transform)
        logger.info(f"Saved transform: {args.output_transform}")

    slicer.mrmlScene.RemoveNode(fixed_node)
    slicer.mrmlScene.RemoveNode(moving_node)
    slicer.mrmlScene.RemoveNode(output_node)
    slicer.mrmlScene.RemoveNode(transform_node)

    logger.info("Registration complete")


def main():
    args = parse_args()
    run_registration(args)


if __name__ == "__main__":
    main()
