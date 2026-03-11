# Automated Pipeline

Reference documentation for the NeuronSegmenter extension and CLI scripts.

## NeuronSegmenter Extension (GUI)

The extension adds a panel to 3D Slicer under **Segmentation > NeuronSegmenter** with the following parameters:

| Parameter | Default | Description |
|---|---|---|
| **Gaussian Sigma** | 1.0 | Smoothing strength. Higher values reduce noise but blur membrane boundaries. |
| **Membrane Threshold** | 128 | Intensity cutoff (0-255 scale). Lower values detect more membrane. |
| **Min Segment Size** | 500 | Minimum voxels per segment. Smaller segments are discarded. |
| **Fill Holes** | On | Fills interior holes in each segment after watershed. |

### Parameter Tuning

- Over-segmentation (too many fragments): increase Min Segment Size or Gaussian Sigma
- Under-segmentation (neurons merged): raise Membrane Threshold or decrease Gaussian Sigma
- Missed membranes: lower Membrane Threshold

## CLI Scripts

All scripts run via `Slicer --python-script` and accept standard argparse flags.

### batch_segment_em.py

```bash
Slicer --python-script scripts/batch_segment_em.py \
    --input-dir ./data/em_stacks \
    --output-dir ./output/labels \
    --sigma 1.0 --threshold 128 --min-size 500
```

Processes every `.nrrd`, `.tiff`, or `.nii` file in the input directory. Outputs one `*_labels.nrrd` label map per volume.

### compute_segment_stats.py

```bash
Slicer --python-script scripts/compute_segment_stats.py \
    --segmentation ./output/labels/sample_labels.nrrd \
    --reference-volume ./data/em_stacks/sample.nrrd \
    --output-csv ./output/stats.csv
```

Outputs a CSV with columns: segment_id, segment_name, voxel_count, volume_mm3, surface_area_mm2, centroid_ras_x/y/z.

### export_neuron_meshes.py

```bash
Slicer --python-script scripts/export_neuron_meshes.py \
    --segmentation ./output/labels/sample_labels.nrrd \
    --output-dir ./output/meshes \
    --format stl --smoothing-iterations 25
```

Produces one `neuron_XXXX.stl` (or `.obj`) per labeled neuron using VTK marching cubes with Laplacian smoothing.

### register_to_atlas.py

```bash
Slicer --python-script scripts/register_to_atlas.py \
    --moving ./data/em_stacks/sample.nrrd \
    --fixed ./data/atlas/reference.nrrd \
    --output-volume ./output/registered.nrrd \
    --output-transform ./output/transform.h5 \
    --registration-type affine
```

Wraps BRAINSFit for rigid, affine, or B-spline registration.
