# Architecture Overview

This document describes how the components of the slicer-connectomics-toolkit fit together.

## High-Level Data Flow

```mermaid
flowchart TD
    subgraph input [Input Data]
        EM[EM Volume Files<br>.nrrd / .tiff / .nii]
        Atlas[Atlas Reference Volume]
    end

    subgraph slicerExt [3D Slicer Extension]
        GUI[NeuronSegmenter GUI Panel]
        Logic[NeuronSegmenterLogic]
        SegLogic[SegmentationLogic<br>preprocess / detect / watershed]
        Morph[MorphologyUtils<br>cleanup / fill / skeleton]
    end

    subgraph scripts [CLI Scripts]
        Batch[batch_segment_em.py]
        Export[export_neuron_meshes.py]
        Stats[compute_segment_stats.py]
        Reg[register_to_atlas.py]
    end

    subgraph outputs [Outputs]
        Labels[Label Maps .nrrd]
        Meshes[3D Meshes .stl / .obj]
        CSV[Statistics .csv]
        RegVol[Registered Volume]
    end

    subgraph analysis [Analysis]
        NB1[Notebook 01: Exploration]
        NB2[Notebook 02: Segmentation]
        NB3[Notebook 03: Morphology]
    end

    EM --> GUI
    GUI --> Logic
    Logic --> SegLogic
    Logic --> Morph
    SegLogic --> Labels
    Morph --> Labels

    EM --> Batch
    Batch --> Logic
    Labels --> Export --> Meshes
    Labels --> Stats --> CSV
    EM --> Reg
    Atlas --> Reg
    Reg --> RegVol

    EM --> NB1
    EM --> NB2
    Labels --> NB3
    CSV --> NB3
```

## Component Responsibilities

### Extension (`extension/NeuronSegmenter/`)

| File | Role |
|------|------|
| `NeuronSegmenter.py` | Slicer module registration, GUI panel (input selectors, parameter sliders, run button), orchestration |
| `SegmentationLogic.py` | Core algorithm: Gaussian smoothing, CLAHE, membrane thresholding, distance-transform watershed, CC labeling |
| `MorphologyUtils.py` | Post-processing: small-object removal, hole filling, morphological smoothing, skeletonization, sequential relabeling |

The extension is a **scripted loadable module** that registers with Slicer's module system. The GUI (`NeuronSegmenterWidget`) creates Qt widgets via Slicer's `ctk` and `qt` bindings. The logic layer (`NeuronSegmenterLogic`) delegates to the library classes and handles conversion between Slicer nodes and numpy arrays.

### Scripts (`scripts/`)

| Script | Input | Output | Slicer Modules Used |
|--------|-------|--------|---------------------|
| `batch_segment_em.py` | Directory of EM volumes | Label maps (.nrrd) | NeuronSegmenter |
| `export_neuron_meshes.py` | Label map | STL/OBJ meshes | VTK (marching cubes) |
| `compute_segment_stats.py` | Label map + reference volume | CSV statistics | SegmentStatistics |
| `register_to_atlas.py` | Moving + fixed volumes | Registered volume + transform | BRAINSFit |

Scripts are designed to run via `Slicer --python-script` so they have access to Slicer's Python environment, VTK, ITK, and all installed modules.

### Notebooks (`notebooks/`)

| Notebook | Purpose | Key Libraries |
|----------|---------|---------------|
| `01_em_volume_exploration` | Load and visualize EM data | pynrrd, nibabel, matplotlib |
| `02_neuron_segmentation_pipeline` | Step-by-step segmentation walkthrough | scipy, scikit-image, cc3d |
| `03_morphology_analysis` | Quantitative neuron metrics and plots | scikit-image, pandas, matplotlib |

Notebooks run in standard Python (outside Slicer) and reproduce the segmentation logic using the same libraries. They serve as documentation and as standalone analysis tools.

## Dependency Graph

```mermaid
flowchart LR
    subgraph slicer [3D Slicer Environment]
        SlicerPy[Slicer Python]
        VTK[VTK]
        ITK[ITK]
        SegStats[SegmentStatistics Module]
        BRAINSFit[BRAINSFit Module]
    end

    subgraph pylibs [Python Libraries]
        NumPy[numpy]
        SciPy[scipy]
        SkImage[scikit-image]
        CC3D[connected-components-3d]
        NiBabel[nibabel]
        PyNRRD[pynrrd]
        MPL[matplotlib]
        PyVista[pyvista]
    end

    SlicerPy --> VTK
    SlicerPy --> ITK
    SlicerPy --> NumPy

    SegLogicNode[SegmentationLogic] --> NumPy
    SegLogicNode --> SciPy
    SegLogicNode --> SkImage
    SegLogicNode --> CC3D

    MorphNode[MorphologyUtils] --> NumPy
    MorphNode --> SciPy
    MorphNode --> SkImage

    NB1Node[Notebooks] --> NumPy
    NB1Node --> MPL
    NB1Node --> NiBabel
    NB1Node --> PyNRRD
    NB1Node --> PyVista
```
