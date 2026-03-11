# Sample Data

## Included Dataset: ISBI 2012

The `isbi2012/` directory contains the ISBI 2012 EM Segmentation Challenge dataset -- 30 serial-section TEM slices of *Drosophila* first instar larva ventral nerve cord with expert-annotated membrane labels.

| File | Description | Resolution |
|---|---|---|
| `train-volume.tif` | 30-slice EM volume (512x512 per slice) | 4x4x50 nm |
| `train-labels.tif` | Ground truth membrane annotations | 4x4x50 nm |
| `test-volume.tif` | 30-slice test volume (no labels) | 4x4x50 nm |
| `test-labels.tif` | Test labels | 4x4x50 nm |

**Source:** [ISBI 2012 Segmentation Challenge](https://imagej.net/events/isbi-2012-segmentation-challenge)
**Download:** [https://downloads.imagej.net/ISBI-2012-challenge.zip](https://downloads.imagej.net/ISBI-2012-challenge.zip)

## Additional Public Datasets

| Dataset | Description | Link |
|---|---|---|
| **CREMI** | 1250x1250x125 EM of *Drosophila* brain (HDF5) | [cremi.org](https://cremi.org/) |
| **SNEMI3D** | 1024x1024x100 EM of mouse cortex (TIFF) | [snemi3d.grand-challenge.org](https://snemi3d.grand-challenge.org/) |
| **EPFL Hippocampus** | 1065x2048x1536 FIB-SEM of mouse CA1 (TIFF) | [epfl.ch](https://www.epfl.ch/labs/cvlab/data/data-em/) |
