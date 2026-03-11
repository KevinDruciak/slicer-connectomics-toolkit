"""
Morphological post-processing utilities for neuron segmentation.

Author: Kevin Druciak (kevintdruciak@gmail.com)

Provides helpers for cleaning up label maps produced by the segmentation
pipeline: small-object removal, hole filling, morphological smoothing,
and optional skeletonization.
"""

import logging

import numpy as np
from scipy.ndimage import (
    binary_fill_holes,
    binary_opening,
    binary_closing,
    generate_binary_structure,
    label as ndi_label,
)

try:
    from skimage.morphology import skeletonize_3d
    HAS_SKELETON = True
except ImportError:
    HAS_SKELETON = False

try:
    import cc3d
    USE_CC3D = True
except ImportError:
    USE_CC3D = False

logger = logging.getLogger(__name__)


class MorphologyUtils:
    """Stateless morphological post-processing for 3D label arrays."""

    def remove_small_objects(
        self, labels: np.ndarray, min_size: int = 500
    ) -> np.ndarray:
        """
        Remove labeled segments smaller than ``min_size`` voxels.

        Parameters
        ----------
        labels : np.ndarray
            Integer label array (0 = background).
        min_size : int
            Minimum number of voxels a segment must contain to survive.

        Returns
        -------
        np.ndarray
            Cleaned label array with small segments set to 0.
        """
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels != 0]
        removed = 0

        for lbl in unique_labels:
            mask = labels == lbl
            if mask.sum() < min_size:
                labels[mask] = 0
                removed += 1

        logger.info(
            f"Removed {removed} segments smaller than {min_size} voxels"
        )
        return labels

    def fill_holes(self, labels: np.ndarray) -> np.ndarray:
        """
        Fill interior holes within each labeled segment.

        Iterates over each unique label, applies binary hole filling,
        and writes the filled mask back. Voxels gained by filling are
        assigned to the surrounding label only if they were previously
        background (0).
        """
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels != 0]

        for lbl in unique_labels:
            mask = labels == lbl
            filled = binary_fill_holes(mask)
            new_voxels = filled & (labels == 0)
            labels[new_voxels] = lbl

        logger.info("Hole filling complete")
        return labels

    def smooth_segments(
        self, labels: np.ndarray, iterations: int = 1
    ) -> np.ndarray:
        """
        Apply morphological opening then closing to each segment to smooth
        boundaries and remove small protrusions.
        """
        struct = generate_binary_structure(3, 1)
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels != 0]

        for lbl in unique_labels:
            mask = labels == lbl
            opened = binary_opening(mask, structure=struct, iterations=iterations)
            closed = binary_closing(opened, structure=struct, iterations=iterations)
            labels[mask & ~closed] = 0
            labels[closed & (labels == 0)] = lbl

        logger.info(f"Morphological smoothing complete (iterations={iterations})")
        return labels

    def skeletonize(self, labels: np.ndarray) -> np.ndarray:
        """
        Compute the 3D skeleton of the foreground (all labeled voxels).

        Useful for extracting neurite centerlines for length measurements.

        Returns
        -------
        np.ndarray
            Binary array where 1 = skeleton voxel.

        Raises
        ------
        RuntimeError
            If scikit-image's ``skeletonize_3d`` is not available.
        """
        if not HAS_SKELETON:
            raise RuntimeError(
                "skeletonize_3d requires scikit-image. "
                "Install it with: pip install scikit-image"
            )
        foreground = (labels > 0).astype(np.uint8)
        skeleton = skeletonize_3d(foreground)
        logger.info(f"Skeletonization: {skeleton.sum()} skeleton voxels")
        return skeleton

    def relabel_sequential(self, labels: np.ndarray) -> np.ndarray:
        """
        Relabel segments sequentially starting from 1 so there are no gaps
        in the label IDs. Background (0) is preserved.
        """
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels != 0]
        new_labels = np.zeros_like(labels)

        for new_id, old_id in enumerate(unique_labels, start=1):
            new_labels[labels == old_id] = new_id

        logger.info(
            f"Relabeled {len(unique_labels)} segments sequentially"
        )
        return new_labels
