# slicer-connectomics-toolkit

**Neuron Segmentation and Connectomics Analysis with 3D Slicer**

A comprehensive toolkit for automated neuron segmentation from electron microscopy (EM) volumes, built on [3D Slicer](https://www.slicer.org/). This repository includes a custom Slicer extension, batch-processing scripts, Jupyter notebooks for analysis, and step-by-step tutorials -- everything needed to go from raw EM image stacks to quantified, visualizable neuron reconstructions.

---

## About

I developed this toolkit during and after my studies at **Johns Hopkins University**, where I took coursework in connectomics that used 3D Slicer as the primary platform for volumetric image analysis. The courses covered EM-based neural circuit reconstruction, manual and semi-automated segmentation workflows, and quantitative morphology -- all within the Slicer ecosystem.

That hands-on experience motivated me to build a reusable, scriptable pipeline that automates the most time-consuming parts of the connectomics workflow while staying fully integrated with Slicer's visualization and data management capabilities.

## Key Features

- **Custom Slicer Extension** -- `NeuronSegmenter` adds a dedicated panel to 3D Slicer for membrane-based neuron segmentation with configurable preprocessing and post-processing
- **Batch Processing** -- segment entire directories of EM stacks from the command line via `Slicer --python-script`
- **Mesh Export** -- extract individual neuron surfaces as STL/OBJ files for downstream analysis or 3D printing
- **Quantitative Metrics** -- compute volume, surface area, and centroid for every segmented neuron, exported as CSV
- **Atlas Registration** -- align EM volumes to a reference coordinate frame using Slicer's registration modules
- **Jupyter Notebooks** -- interactive exploration, segmentation walkthroughs, and morphology analysis outside of Slicer
- **Tutorials** -- four Markdown guides covering installation, manual segmentation, the automated pipeline, and visualization/export

## Repository Structure

```
slicer-connectomics-toolkit/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── extension/                       # Custom 3D Slicer Extension
│   └── NeuronSegmenter/
│       ├── CMakeLists.txt
│       ├── NeuronSegmenter.py
│       ├── NeuronSegmenterLib/
│       │   ├── __init__.py
│       │   ├── SegmentationLogic.py
│       │   └── MorphologyUtils.py
│       ├── Resources/Icons/
│       └── Testing/
│           └── test_segmentation.py
│
├── scripts/
│   ├── batch_segment_em.py
│   ├── export_neuron_meshes.py
│   ├── compute_segment_stats.py
│   └── register_to_atlas.py
│
├── notebooks/
│   ├── 01_em_volume_exploration.ipynb
│   ├── 02_neuron_segmentation_pipeline.ipynb
│   └── 03_morphology_analysis.ipynb
│
├── tutorials/
│   ├── 01_getting_started.md
│   ├── 02_manual_segmentation.md
│   ├── 03_automated_pipeline.md
│   └── 04_visualization_and_export.md
│
├── sample_data/
│   └── README.md
│
└── docs/
    ├── architecture.md
    └── references.md
```

## Quick Start

### Prerequisites

- [3D Slicer](https://download.slicer.org/) 5.2 or later
- Python 3.9+ (bundled with Slicer; standalone Python needed only for notebooks)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/slicer-connectomics-toolkit.git
cd slicer-connectomics-toolkit
```

### 2. Install Python Dependencies (for notebooks)

```bash
pip install -r requirements.txt
```

### 3. Load the Extension in 3D Slicer

1. Open 3D Slicer
2. Go to **Edit > Application Settings > Modules**
3. Add the path to `extension/NeuronSegmenter/` as an additional module path
4. Restart Slicer -- the **NeuronSegmenter** module will appear under the *Segmentation* category

### 4. Run a Script

```bash
/path/to/Slicer --python-script scripts/batch_segment_em.py --input-dir ./sample_data --output-dir ./output
```

### 5. Explore the Notebooks

```bash
jupyter notebook notebooks/
```

## Datasets

This toolkit is designed to work with publicly available EM segmentation benchmarks:

| Dataset | Description | Link |
|---------|-------------|------|
| **CREMI** | Challenge on circuit reconstruction from EM images | [cremi.org](https://cremi.org/) |
| **SNEMI3D** | 3D segmentation of neurites in EM images | [snemi3d.grand-challenge.org](https://snemi3d.grand-challenge.org/) |
| **ISBI 2012** | EM segmentation challenge (serial section TEM) | [ISBI Challenge](https://imagej.net/events/isbi-2012-segmentation-challenge) |

A minimal synthetic test volume (`mini_em_stack.nrrd`) is included in `sample_data/` for quick testing. See [`sample_data/README.md`](sample_data/README.md) for download instructions for full datasets.

## Technology Stack

| Component | Role |
|-----------|------|
| [3D Slicer](https://www.slicer.org/) | Platform for visualization, segmentation, and registration |
| [VTK](https://vtk.org/) | Mesh generation and 3D rendering |
| [ITK](https://itk.org/) | Image filtering and registration backends |
| [scikit-image](https://scikit-image.org/) | Watershed, morphology, and connected components |
| [connected-components-3d](https://github.com/seung-lab/connected-components-3d) | Fast 3D connected-component labeling |
| [nibabel](https://nipy.org/nibabel/) / [pynrrd](https://github.com/mhe/pynrrd) | Reading/writing NIfTI and NRRD volumes |
| [matplotlib](https://matplotlib.org/) / [pyvista](https://docs.pyvista.org/) | 2D/3D visualization in notebooks |

## Screenshots

> *Screenshots will be added after running the pipeline on sample data.*

| EM Slice with Overlay | 3D Neuron Rendering | Segmentation Metrics |
|:---------------------:|:-------------------:|:--------------------:|
| *coming soon* | *coming soon* | *coming soon* |

## Tutorials

1. [Getting Started](tutorials/01_getting_started.md) -- installation, loading data, first look
2. [Manual Segmentation](tutorials/02_manual_segmentation.md) -- using Segment Editor for ground truth
3. [Automated Pipeline](tutorials/03_automated_pipeline.md) -- running batch segmentation scripts
4. [Visualization and Export](tutorials/04_visualization_and_export.md) -- volume rendering, mesh export, figures

## Documentation

- [Architecture Overview](docs/architecture.md) -- how the extension, scripts, and notebooks fit together
- [References](docs/references.md) -- academic papers, Slicer documentation, and course materials

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- The [3D Slicer](https://www.slicer.org/) community and the Slicer developer documentation
- Johns Hopkins University Department of Biomedical Engineering for connectomics coursework
- The CREMI, SNEMI3D, and ISBI 2012 challenge organizers for public benchmark datasets
- Funke et al., Turaga et al., and the broader connectomics research community
