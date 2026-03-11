# Manual Segmentation with Segment Editor

This tutorial covers how to use 3D Slicer's built-in **Segment Editor** to manually segment neurons in EM data. Manual segmentation is essential for creating ground truth labels and understanding the data before running automated pipelines.

## Why Manual Segmentation?

- Builds intuition for what good segmentation looks like
- Creates ground truth for validating automated methods
- Handles edge cases that automated methods may miss
- Required for training supervised segmentation models

## 1. Open Segment Editor

1. Load an EM volume (see [Getting Started](01_getting_started.md))
2. Switch to the **Segment Editor** module (under **Segmentation** in the module dropdown)
3. Click **Add** to create a new segmentation node
4. Click the **+** button to add a new segment (e.g., "Neuron_1")

## 2. Key Tools

### Paint

- Select the **Paint** effect from the toolbar
- Adjust the brush diameter using the slider
- Left-click and drag to paint on a slice
- Works in any slice orientation (axial, coronal, sagittal)

**Tip:** Use a small brush near membranes and a larger brush for cell interiors.

### Threshold

- Select the **Threshold** effect
- Adjust the intensity range to capture cell interiors (bright regions)
- Click **Apply** to fill the current segment with all voxels in the threshold range

**Tip:** Start with a wide range and narrow it down. For EM data, cell interiors are typically in the upper half of the intensity range.

### Grow from Seeds

This is the most efficient tool for neuron segmentation:

1. Create one segment per neuron you want to label
2. Use **Paint** to place a small seed (a few voxels) inside each neuron
3. Create a "Background" segment and paint seeds on the membranes
4. Select the **Grow from Seeds** effect
5. Click **Initialize** to see a preview
6. Adjust seeds if needed, then click **Apply**

The algorithm uses a competition-based region growing that respects intensity boundaries -- ideal for EM membrane detection.

### Islands

After thresholding, you may have one large connected region. The **Islands** effect lets you:

- **Keep largest island** -- useful for isolating the main tissue region
- **Split islands to segments** -- automatically assigns each disconnected region to a separate segment
- **Remove small islands** -- cleans up noise

### Scissors

- Use **Scissors** to cut away unwanted regions
- Choose between **Erase inside** and **Erase outside**
- Useful for trimming segments that bleed across membranes

## 3. Workflow for EM Neuron Segmentation

A recommended workflow for manually segmenting a few neurons:

1. **Scroll through the volume** to identify 3-5 neurons you want to segment
2. **Create segments** -- one per neuron, plus a "Background" segment
3. **Place seeds** using Paint:
   - Small dots inside each target neuron
   - A line along visible membranes for the background
4. **Run Grow from Seeds** and inspect the result
5. **Refine** with Paint and Scissors where boundaries are incorrect
6. **Repeat** slice by slice if needed, or let the 3D growth handle interpolation

## 4. Saving Your Work

- Segmentations are saved automatically with the Slicer scene (**File > Save**)
- To export as a label map: right-click the segmentation in the **Data** module and select **Export to file**
- Supported export formats: NRRD, NIfTI, STL (surfaces)

## 5. Tips for EM Data

- **Zoom in** -- EM data is high resolution; work at high zoom for accurate boundaries
- **Use all three slice views** -- membranes that are ambiguous in one orientation may be clear in another
- **Adjust window/level** -- increase contrast to make faint membranes visible
- **Save frequently** -- manual segmentation is time-consuming; save your scene regularly

## Next Steps

- [Automated Pipeline](03_automated_pipeline.md) -- automate what you just did manually
- [Visualization and Export](04_visualization_and_export.md) -- render and export your segmentations
