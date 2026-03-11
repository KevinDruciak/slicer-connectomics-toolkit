# Getting Started

This guide walks you through installing 3D Slicer, loading the NeuronSegmenter extension, and opening your first EM volume.

## Prerequisites

- A computer running Windows 10+, macOS 11+, or Ubuntu 20.04+
- At least 8 GB of RAM (16 GB recommended for large volumes)
- A GPU is helpful for volume rendering but not required

## 1. Install 3D Slicer

1. Go to [https://download.slicer.org/](https://download.slicer.org/)
2. Download the **Stable Release** (version 5.2 or later) for your operating system
3. Run the installer and follow the prompts
4. Launch 3D Slicer to verify the installation

## 2. Clone This Repository

```bash
git clone https://github.com/<your-username>/slicer-connectomics-toolkit.git
cd slicer-connectomics-toolkit
```

## 3. Add the NeuronSegmenter Module

1. In 3D Slicer, go to **Edit > Application Settings > Modules**
2. Under **Additional module paths**, click **Add**
3. Browse to the `extension/NeuronSegmenter/` directory inside this repository
4. Click **OK** and restart 3D Slicer when prompted

After restarting, you should see **NeuronSegmenter** listed under the **Segmentation** module category in the module dropdown.

## 4. Load Sample Data

### Option A: Use the included mini volume

1. In Slicer, go to **File > Add Data**
2. Navigate to `sample_data/mini_em_stack.nrrd` in this repository
3. Click **OK** to load

### Option B: Download a public dataset

See [`sample_data/README.md`](../sample_data/README.md) for links to CREMI, SNEMI3D, and ISBI 2012 datasets. After downloading:

1. Go to **File > Add Data**
2. Select the downloaded `.nrrd`, `.tiff`, or `.nii.gz` file
3. Click **OK** to load

## 5. First Look

Once the volume is loaded:

- Use the **slice viewers** (red, green, yellow panels) to scroll through the EM stack
- Adjust **Window/Level** by holding the left mouse button and dragging in a slice view
- Use the **3D view** (blue panel) to see a volume rendering -- you may need to enable it in the **Volume Rendering** module

## 6. Verify the Extension

1. Open the module dropdown and select **Segmentation > NeuronSegmenter**
2. You should see the NeuronSegmenter panel with:
   - An **Input** section with a volume selector
   - A **Segmentation Parameters** section with sliders for Gaussian sigma, membrane threshold, and minimum segment size
   - An **Output** section with a segmentation selector
   - A **Run Segmentation** button

If you see this panel, the extension is installed correctly and you are ready to proceed.

## Next Steps

- [Manual Segmentation](02_manual_segmentation.md) -- learn to use Slicer's Segment Editor for ground truth
- [Automated Pipeline](03_automated_pipeline.md) -- run the batch segmentation scripts
