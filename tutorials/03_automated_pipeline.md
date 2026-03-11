# Automated Segmentation Pipeline

This tutorial explains how to use the NeuronSegmenter extension and the batch processing scripts to segment EM volumes automatically.

## Option 1: Interactive (GUI)

### Using the NeuronSegmenter Extension

1. Load your EM volume in 3D Slicer
2. Switch to **Segmentation > NeuronSegmenter** in the module dropdown
3. Configure parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| **Gaussian Sigma** | 1.0 | Smoothing strength. Increase for noisy data. |
| **Membrane Threshold** | 128 | Intensity cutoff (0-255). Lower = more membrane detected. |
| **Min Segment Size** | 500 | Voxels. Segments smaller than this are discarded. |
| **Fill Holes** | On | Fill interior holes in each segment. |

4. Select your input volume in the **Input EM Volume** dropdown
5. Optionally select or create an output segmentation node
6. Click **Run Segmentation**
7. Inspect the result in the slice views and 3D view

### Tuning Parameters

- **Too many small fragments?** Increase **Min Segment Size** or increase **Gaussian Sigma**
- **Membranes not detected?** Lower the **Membrane Threshold**
- **Neurons merged together?** Raise the **Membrane Threshold** or decrease **Gaussian Sigma**
- **Holes inside neurons?** Make sure **Fill Holes** is checked

## Option 2: Command Line (Batch Processing)

### batch_segment_em.py

Process an entire directory of EM volumes:

```bash
/path/to/Slicer --python-script scripts/batch_segment_em.py \
    --input-dir /data/em_stacks \
    --output-dir /data/segmented \
    --sigma 1.0 \
    --threshold 128 \
    --min-size 500
```

**Arguments:**

| Flag | Required | Description |
|------|----------|-------------|
| `--input-dir` | Yes | Directory with `.nrrd`, `.tiff`, or `.nii` files |
| `--output-dir` | Yes | Where to save label maps |
| `--sigma` | No | Gaussian sigma (default: 1.0) |
| `--threshold` | No | Membrane threshold (default: 128) |
| `--min-size` | No | Minimum segment size (default: 500) |

**Output:** One `*_labels.nrrd` file per input volume.

### compute_segment_stats.py

After segmentation, compute per-neuron metrics:

```bash
/path/to/Slicer --python-script scripts/compute_segment_stats.py \
    --segmentation /data/segmented/sample_labels.nrrd \
    --reference-volume /data/em_stacks/sample.nrrd \
    --output-csv /data/results/stats.csv
```

The output CSV contains: segment ID, name, voxel count, volume (mm^3), surface area (mm^2), and centroid coordinates.

### export_neuron_meshes.py

Export each neuron as a 3D surface mesh:

```bash
/path/to/Slicer --python-script scripts/export_neuron_meshes.py \
    --segmentation /data/segmented/sample_labels.nrrd \
    --output-dir /data/meshes \
    --format stl \
    --smoothing-iterations 25
```

This produces one `neuron_XXXX.stl` (or `.obj`) file per labeled neuron.

### register_to_atlas.py

Align an EM volume to a reference coordinate frame:

```bash
/path/to/Slicer --python-script scripts/register_to_atlas.py \
    --moving /data/em_stacks/sample.nrrd \
    --fixed /data/atlas/reference.nrrd \
    --output-volume /data/registered/sample_registered.nrrd \
    --output-transform /data/registered/transform.h5 \
    --registration-type affine
```

## Full Pipeline Example

A typical end-to-end workflow:

```bash
INPUT=/data/em_stacks
OUTPUT=/data/results
SLICER=/path/to/Slicer

# 1. Segment all volumes
$SLICER --python-script scripts/batch_segment_em.py \
    --input-dir $INPUT --output-dir $OUTPUT/labels

# 2. Compute statistics
for f in $OUTPUT/labels/*.nrrd; do
    base=$(basename "$f" _labels.nrrd)
    $SLICER --python-script scripts/compute_segment_stats.py \
        --segmentation "$f" \
        --reference-volume "$INPUT/${base}.nrrd" \
        --output-csv "$OUTPUT/stats/${base}_stats.csv"
done

# 3. Export meshes
for f in $OUTPUT/labels/*.nrrd; do
    base=$(basename "$f" _labels.nrrd)
    $SLICER --python-script scripts/export_neuron_meshes.py \
        --segmentation "$f" \
        --output-dir "$OUTPUT/meshes/$base" \
        --format stl
done
```

## Next Steps

- [Visualization and Export](04_visualization_and_export.md) -- render results and create figures
- [Notebooks](../notebooks/) -- interactive analysis in Jupyter
