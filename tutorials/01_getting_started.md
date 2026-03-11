# Getting Started

Prerequisites and setup for the slicer-connectomics-toolkit.

## Requirements

- [3D Slicer](https://download.slicer.org/) 5.2+
- Python 3.9+ (bundled with Slicer; standalone Python needed only for notebooks)
- 8 GB RAM minimum, 16 GB recommended for large EM volumes

## Setup

```bash
git clone https://github.com/KevinDruciak/slicer-connectomics-toolkit.git
cd slicer-connectomics-toolkit
pip install -r requirements.txt
```

## Loading the NeuronSegmenter Extension

1. In 3D Slicer: **Edit > Application Settings > Modules**
2. Add `extension/NeuronSegmenter/` as an additional module path
3. Restart Slicer

The **NeuronSegmenter** module appears under the **Segmentation** category with an input volume selector, parameter controls (Gaussian sigma, membrane threshold, minimum segment size, hole filling), an output segmentation selector, and a run button.

## Loading Data

Load any `.nrrd`, `.tiff`, or `.nii.gz` EM volume via **File > Add Data**. A synthetic test volume is generated automatically by the notebooks if no real data is available. See [`sample_data/README.md`](../sample_data/README.md) for links to public benchmark datasets.
