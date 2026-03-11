# Visualization and Export

This tutorial covers how to visualize segmentation results in 3D Slicer and export publication-quality figures and meshes.

## 1. Viewing Segmentations in Slice Views

After running the NeuronSegmenter (or loading a label map):

1. Open the **Data** module to see your segmentation node
2. Click the **eye icon** next to the segmentation to toggle visibility
3. In the slice views, segmentation overlays appear as colored regions on top of the EM volume
4. Adjust overlay opacity:
   - Click the **pin icon** in any slice view toolbar to show the slice controls
   - Use the **Segmentation opacity** slider to blend between the EM image and the segmentation

### Changing Segment Colors

1. Open the **Segmentations** module
2. Select your segmentation node
3. Click on a segment in the list
4. Click the **color swatch** to change its display color
5. Use distinct colors for adjacent neurons to improve visual clarity

## 2. 3D Volume Rendering

### Rendering the EM Volume

1. Switch to the **Volume Rendering** module
2. Select your EM volume in the dropdown
3. Click the **eye icon** to enable rendering
4. Choose a preset:
   - **CT-Bones** works reasonably well for EM data (shows dense structures)
   - For better results, create a custom transfer function:
     - Set low intensities (membranes) to semi-transparent
     - Set high intensities (cell interiors) to opaque with a color

### Rendering Segmentations in 3D

1. In the **Data** module, find your segmentation node
2. Click the **eye icon** -- segments automatically appear as 3D surfaces
3. To adjust surface quality:
   - Open the **Segmentations** module
   - Under **Representations**, select **Closed surface**
   - Adjust **Smoothing factor** (higher = smoother surfaces, but slower)

### Combining Views

For the best visualization:

1. Show the EM volume as a semi-transparent volume rendering
2. Overlay the segmentation surfaces in 3D
3. Use **Crop Volume** to focus on a region of interest
4. Rotate the 3D view to find an informative angle

## 3. Exporting Meshes

### From 3D Slicer

1. Right-click the segmentation in the **Data** module
2. Select **Export visible segments to models**
3. Each segment becomes a separate model node
4. Right-click a model > **Export to file** > choose STL or OBJ

### Using the Script

```bash
/path/to/Slicer --python-script scripts/export_neuron_meshes.py \
    --segmentation /path/to/labels.nrrd \
    --output-dir /path/to/meshes \
    --format stl
```

The exported meshes can be:
- Opened in [MeshLab](https://www.meshlab.net/) or [Blender](https://www.blender.org/) for further editing
- Used in [ParaView](https://www.paraview.org/) for scientific visualization
- 3D printed for physical models of neural tissue

## 4. Capturing Screenshots

### High-Resolution Screenshots

1. Go to **View > Screenshot** (or press `Ctrl+Shift+S`)
2. Choose the view to capture (3D view, slice views, or full layout)
3. Set the **Scale factor** (2x or 3x for publication resolution)
4. Click **Save** to export as PNG

### Programmatic Screenshots

In Slicer's Python console:

```python
import ScreenCapture
cap = ScreenCapture.ScreenCaptureLogic()

# Capture the 3D view
cap.captureImageFromView(
    slicer.app.layoutManager().threeDWidget(0).threeDView(),
    "/path/to/output/3d_view.png"
)

# Capture a slice view
cap.captureImageFromView(
    slicer.app.layoutManager().sliceWidget("Red").sliceView(),
    "/path/to/output/axial_view.png"
)
```

## 5. Creating Figures for Publications

### Recommended Layout

A typical connectomics figure includes:

1. **Panel A:** Raw EM slice with scale bar
2. **Panel B:** Same slice with segmentation overlay
3. **Panel C:** 3D rendering of segmented neurons
4. **Panel D:** Quantitative metrics (bar chart or table)

### Adding Scale Bars

1. Slicer displays a ruler in slice views by default
2. For custom scale bars, use the **Markups** module to place a line annotation
3. Alternatively, add scale bars in post-processing (e.g., in Inkscape or Illustrator)

### Export Tips

- Use **PNG** for raster figures (screenshots, slice views)
- Use **SVG** for vector figures (charts, diagrams) -- generate these from the Jupyter notebooks
- Export meshes as **OBJ** for Blender rendering with custom lighting and materials
- Target **300 DPI** minimum for print publications

## 6. Animation

For presentations, create a rotation animation of the 3D view:

```python
import ScreenCapture
cap = ScreenCapture.ScreenCaptureLogic()

view = slicer.app.layoutManager().threeDWidget(0).threeDView()
cap.captureImageFromView(view, "/tmp/frame.png")

# Rotate and capture frames
for angle in range(0, 360, 5):
    view.yaw(5)
    view.forceRender()
    cap.captureImageFromView(view, f"/tmp/rotation_{angle:03d}.png")
```

Then combine frames into a video using ffmpeg:

```bash
ffmpeg -framerate 24 -i /tmp/rotation_%03d.png -c:v libx264 -pix_fmt yuv420p rotation.mp4
```

## Next Steps

- Review the [Jupyter notebooks](../notebooks/) for generating publication-quality plots
- See [Architecture Overview](../docs/architecture.md) for how all components fit together
