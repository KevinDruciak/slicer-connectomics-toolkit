"""
Core segmentation logic for the NeuronSegmenter extension.

Pipeline:
  1. Gaussian smoothing to reduce acquisition noise
  2. Histogram equalization for consistent contrast
  3. Membrane detection via intensity thresholding and edge enhancement
  4. Distance-transform watershed to partition the interior into neuron labels
  5. Connected-component labeling for final per-neuron IDs
"""

import logging

import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt, label as ndi_label
from skimage.exposure import equalize_adapthist
from skimage.segmentation import watershed
from skimage.feature import peak_local_max

try:
    import cc3d
    USE_CC3D = True
except ImportError:
    USE_CC3D = False

logger = logging.getLogger(__name__)


class NeuronSegmentationLogic:
    """Stateless helper that runs the EM neuron segmentation pipeline."""

    def preprocess(self, volume: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """
        Smooth and normalize an EM volume.

        Parameters
        ----------
        volume : np.ndarray
            3D array (Z, Y, X) of uint8 or uint16 intensities.
        sigma : float
            Standard deviation for Gaussian smoothing.

        Returns
        -------
        np.ndarray
            Preprocessed volume with float64 values in [0, 1].
        """
        logger.info(f"Preprocessing: Gaussian sigma={sigma}")
        smoothed = gaussian_filter(volume.astype(np.float64), sigma=sigma)

        chunk_size = max(1, min(volume.shape) // 4)
        equalized = equalize_adapthist(
            smoothed, kernel_size=chunk_size, clip_limit=0.03
        )
        return equalized

    def detect_membranes(
        self, volume: np.ndarray, threshold: int = 128
    ) -> np.ndarray:
        """
        Create a binary membrane mask.

        In EM images of neural tissue, membranes typically appear as dark
        boundaries. Pixels with intensity below the threshold (after
        rescaling to 0-255) are classified as membrane.

        Returns
        -------
        np.ndarray
            Boolean array where True = membrane.
        """
        rescaled = (volume * 255).astype(np.uint8)
        membrane_mask = rescaled < threshold
        logger.info(
            f"Membrane detection: threshold={threshold}, "
            f"membrane fraction={membrane_mask.mean():.3f}"
        )
        return membrane_mask

    def watershed_segment(self, membrane_mask: np.ndarray) -> np.ndarray:
        """
        Partition non-membrane regions into labeled neuron segments using
        a distance-transform seeded watershed.

        Parameters
        ----------
        membrane_mask : np.ndarray
            Boolean array where True = membrane.

        Returns
        -------
        np.ndarray
            Integer label array (0 = membrane/background).
        """
        interior = ~membrane_mask
        distance = distance_transform_edt(interior)

        min_distance = max(5, int(0.02 * min(membrane_mask.shape)))
        coords = peak_local_max(
            distance, min_distance=min_distance, labels=interior.astype(int)
        )

        markers = np.zeros_like(membrane_mask, dtype=np.int32)
        for i, coord in enumerate(coords, start=1):
            markers[tuple(coord)] = i

        labels = watershed(-distance, markers, mask=interior)
        logger.info(f"Watershed produced {labels.max()} initial segments")
        return labels

    def connected_component_relabel(self, labels: np.ndarray) -> np.ndarray:
        """
        Re-label segments using connected-component analysis to ensure
        each spatially disconnected region gets a unique ID.
        """
        if USE_CC3D:
            relabeled = cc3d.connected_components(labels, connectivity=6)
            logger.info(f"CC3D relabeling: {relabeled.max()} components")
        else:
            relabeled, num_features = ndi_label(labels > 0)
            logger.info(f"scipy relabeling: {num_features} components")
        return relabeled

    def segment_neurons(
        self, preprocessed_volume: np.ndarray, membrane_threshold: int = 128
    ) -> np.ndarray:
        """
        End-to-end segmentation: membrane detection -> watershed -> relabel.

        Parameters
        ----------
        preprocessed_volume : np.ndarray
            Output of ``preprocess()``, float64 in [0, 1].
        membrane_threshold : int
            Threshold for membrane detection (0-255 scale).

        Returns
        -------
        np.ndarray
            Integer label array with unique IDs per neuron.
        """
        membrane_mask = self.detect_membranes(preprocessed_volume, membrane_threshold)
        labels = self.watershed_segment(membrane_mask)
        labels = self.connected_component_relabel(labels)
        return labels
