"""
Tests for the NeuronSegmenter extension.

Author: Kevin Druciak (kevintdruciak@gmail.com)

These tests validate the segmentation pipeline using synthetic EM-like
volumes. They can be run:

  1. Inside 3D Slicer's Python console:
       exec(open("path/to/test_segmentation.py").read())

  2. Via pytest (outside Slicer, tests that don't need Slicer nodes):
       pytest test_segmentation.py -v

  3. As a Slicer self-test (registered via ScriptedLoadableModuleTest)
"""

import unittest
import numpy as np


def make_synthetic_em_volume(shape=(32, 64, 64), membrane_spacing=16,
                             membrane_width=2, seed=42):
    """
    Create a synthetic EM-like volume with bright cell interiors and dark
    membrane boundaries arranged in a grid pattern.

    Returns the volume and the expected approximate number of cells.
    """
    rng = np.random.RandomState(seed)
    volume = rng.randint(140, 220, size=shape, dtype=np.uint8)

    for offset in range(membrane_width):
        y_indices = np.arange(offset, shape[1], membrane_spacing)
        x_indices = np.arange(offset, shape[2], membrane_spacing)
        volume[:, y_indices, :] = rng.randint(
            10, 60, size=(shape[0], len(y_indices), shape[2])
        ).astype(np.uint8)
        volume[:, :, x_indices] = rng.randint(
            10, 60, size=(shape[0], shape[1], len(x_indices))
        ).astype(np.uint8)

    cells_y = (shape[1] - membrane_width) // membrane_spacing
    cells_x = (shape[2] - membrane_width) // membrane_spacing
    expected_cells = cells_y * cells_x

    return volume, expected_cells


class TestSegmentationLogic(unittest.TestCase):
    """Test the core segmentation pipeline (no Slicer dependency)."""

    @classmethod
    def setUpClass(cls):
        from NeuronSegmenterLib.SegmentationLogic import NeuronSegmentationLogic
        cls.logic = NeuronSegmentationLogic()
        cls.volume, cls.expected_cells = make_synthetic_em_volume()

    def test_preprocess_output_range(self):
        """Preprocessed volume should be float64 in [0, 1]."""
        result = self.logic.preprocess(self.volume, sigma=1.0)
        self.assertEqual(result.dtype, np.float64)
        self.assertGreaterEqual(result.min(), 0.0)
        self.assertLessEqual(result.max(), 1.0)

    def test_preprocess_preserves_shape(self):
        """Preprocessing should not change the volume shape."""
        result = self.logic.preprocess(self.volume, sigma=1.0)
        self.assertEqual(result.shape, self.volume.shape)

    def test_membrane_detection(self):
        """Membrane mask should be boolean and detect a reasonable fraction."""
        preprocessed = self.logic.preprocess(self.volume, sigma=0.5)
        mask = self.logic.detect_membranes(preprocessed, threshold=128)
        self.assertEqual(mask.dtype, bool)
        fraction = mask.mean()
        self.assertGreater(fraction, 0.01, "Too few membrane voxels detected")
        self.assertLess(fraction, 0.90, "Too many membrane voxels detected")

    def test_watershed_produces_labels(self):
        """Watershed should produce a non-trivial label array."""
        preprocessed = self.logic.preprocess(self.volume, sigma=0.5)
        mask = self.logic.detect_membranes(preprocessed, threshold=128)
        labels = self.logic.watershed_segment(mask)
        self.assertEqual(labels.shape, self.volume.shape)
        self.assertGreater(labels.max(), 0, "No segments produced")

    def test_full_pipeline_segment_count(self):
        """Full pipeline should produce a reasonable number of segments."""
        preprocessed = self.logic.preprocess(self.volume, sigma=0.5)
        labels = self.logic.segment_neurons(preprocessed, membrane_threshold=128)
        n_segments = len(np.unique(labels)) - 1  # exclude background
        self.assertGreater(n_segments, 0, "No segments found")
        self.assertGreater(
            n_segments, self.expected_cells * 0.3,
            f"Too few segments: {n_segments} (expected ~{self.expected_cells})"
        )


class TestMorphologyUtils(unittest.TestCase):
    """Test morphological post-processing utilities."""

    @classmethod
    def setUpClass(cls):
        from NeuronSegmenterLib.MorphologyUtils import MorphologyUtils
        cls.morph = MorphologyUtils()

    def test_remove_small_objects(self):
        """Small objects should be removed, large ones preserved."""
        labels = np.zeros((10, 10, 10), dtype=np.int32)
        labels[0:2, 0:2, 0:2] = 1   # 8 voxels
        labels[5:10, 5:10, 5:10] = 2  # 125 voxels

        result = self.morph.remove_small_objects(labels.copy(), min_size=50)
        self.assertEqual((result == 1).sum(), 0, "Small object was not removed")
        self.assertGreater((result == 2).sum(), 0, "Large object was removed")

    def test_fill_holes(self):
        """Interior holes should be filled."""
        labels = np.zeros((10, 10, 10), dtype=np.int32)
        labels[1:9, 1:9, 1:9] = 1
        labels[3:7, 3:7, 3:7] = 0  # interior hole

        result = self.morph.fill_holes(labels.copy())
        self.assertTrue(
            np.all(result[3:7, 3:7, 3:7] == 1),
            "Hole was not filled"
        )

    def test_relabel_sequential(self):
        """Labels should be renumbered sequentially with no gaps."""
        labels = np.zeros((5, 5, 5), dtype=np.int32)
        labels[0:2, :, :] = 5
        labels[3:5, :, :] = 20

        result = self.morph.relabel_sequential(labels)
        unique = set(np.unique(result))
        self.assertEqual(unique, {0, 1, 2})

    def test_remove_small_preserves_background(self):
        """Background (label 0) should never be removed."""
        labels = np.zeros((10, 10, 10), dtype=np.int32)
        labels[5:10, 5:10, 5:10] = 1

        result = self.morph.remove_small_objects(labels.copy(), min_size=50)
        self.assertEqual((result == 0).sum(), 10**3 - 125)


if __name__ == "__main__":
    unittest.main(verbosity=2)
