# Manual Segmentation Workflow

This document describes the manual segmentation approach I used to create ground truth labels for validating the automated pipeline. Manual annotation serves as the baseline for evaluating segmentation accuracy and is necessary for training supervised models.

## Approach

I used 3D Slicer's **Segment Editor** module with the following tool combination:

1. **Grow from Seeds** -- the primary tool. I placed small paint seeds inside each target neuron and along membranes (as background), then ran the competition-based region growing. This respects intensity boundaries and works well for EM membrane detection.

2. **Paint + Scissors** -- for refinement. Where automated growth bled across faint membranes, I corrected boundaries manually using paint (small brush near membranes, larger brush for interiors) and scissors to trim overflows.

3. **Islands** -- for post-processing. After thresholding, I used "Split islands to segments" to automatically assign each disconnected region to a separate segment, then "Remove small islands" to clean up noise.

## Typical Workflow

For a given EM volume, I would:

1. Scroll through the stack to identify target neurons
2. Create one segment per neuron plus a background segment
3. Place seeds using Paint in all three slice orientations (axial, coronal, sagittal) -- membranes that are ambiguous in one view are often clear in another
4. Run Grow from Seeds, inspect the result, and refine
5. Export the final segmentation as a label map (NRRD) for use with the automated pipeline and statistics scripts

## Notes on EM Data

- Working at high zoom is essential -- EM resolution is much finer than the display
- Adjusting window/level to increase contrast makes faint membranes visible
- Segmentations are saved with the Slicer scene and can be exported as NRRD, NIfTI, or STL
