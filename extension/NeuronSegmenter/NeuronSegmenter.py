"""
NeuronSegmenter -- 3D Slicer scripted module for automated neuron segmentation
from electron microscopy (EM) volumes.

Author: Kevin Druciak (kevintdruciak@gmail.com)

Provides a GUI panel for configuring preprocessing parameters, running
membrane-based watershed segmentation, and applying morphological cleanup.
"""

import os
import logging

import slicer
from slicer.ScriptedLoadableModule import (
    ScriptedLoadableModule,
    ScriptedLoadableModuleWidget,
    ScriptedLoadableModuleLogic,
    ScriptedLoadableModuleTest,
)
from slicer.util import VTKObservationMixin
import qt
import vtk

from NeuronSegmenterLib.SegmentationLogic import NeuronSegmentationLogic
from NeuronSegmenterLib.MorphologyUtils import MorphologyUtils


class NeuronSegmenter(ScriptedLoadableModule):
    """Module descriptor registered with 3D Slicer."""

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "NeuronSegmenter"
        self.parent.categories = ["Segmentation"]
        self.parent.dependencies = []
        self.parent.contributors = ["Kevin Druciak (Johns Hopkins University)"]
        self.parent.helpText = (
            "Automated neuron segmentation from EM volumes using membrane "
            "detection, watershed partitioning, and morphological cleanup. "
            "See <a href='https://github.com/KevinDruciak/slicer-connectomics-toolkit'>the repository</a> for details."
        )
        self.parent.acknowledgementText = (
            "Developed as part of connectomics coursework at Johns Hopkins "
            "University. Built on 3D Slicer, ITK, VTK, and scikit-image."
        )


class NeuronSegmenterWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """GUI panel that appears in 3D Slicer when the module is selected."""

    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = NeuronSegmenterLogic()

        # --- Input section ---
        inputCollapsible = ctk.ctkCollapsibleButton()
        inputCollapsible.text = "Input"
        self.layout.addWidget(inputCollapsible)
        inputLayout = qt.QFormLayout(inputCollapsible)

        self.inputVolumeSelector = slicer.qMRMLNodeComboBox()
        self.inputVolumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.inputVolumeSelector.selectNodeUponCreation = True
        self.inputVolumeSelector.addEnabled = False
        self.inputVolumeSelector.removeEnabled = False
        self.inputVolumeSelector.noneEnabled = True
        self.inputVolumeSelector.showHidden = False
        self.inputVolumeSelector.setMRMLScene(slicer.mrmlScene)
        self.inputVolumeSelector.setToolTip("Select the input EM volume.")
        inputLayout.addRow("Input EM Volume:", self.inputVolumeSelector)

        # --- Parameters section ---
        paramsCollapsible = ctk.ctkCollapsibleButton()
        paramsCollapsible.text = "Segmentation Parameters"
        self.layout.addWidget(paramsCollapsible)
        paramsLayout = qt.QFormLayout(paramsCollapsible)

        self.gaussianSigmaSlider = ctk.ctkSliderWidget()
        self.gaussianSigmaSlider.singleStep = 0.1
        self.gaussianSigmaSlider.minimum = 0.1
        self.gaussianSigmaSlider.maximum = 5.0
        self.gaussianSigmaSlider.value = 1.0
        self.gaussianSigmaSlider.setToolTip(
            "Standard deviation for Gaussian smoothing before membrane detection."
        )
        paramsLayout.addRow("Gaussian Sigma:", self.gaussianSigmaSlider)

        self.membraneThresholdSlider = ctk.ctkSliderWidget()
        self.membraneThresholdSlider.singleStep = 1
        self.membraneThresholdSlider.minimum = 0
        self.membraneThresholdSlider.maximum = 255
        self.membraneThresholdSlider.value = 128
        self.membraneThresholdSlider.setToolTip(
            "Intensity threshold for membrane detection. Pixels below this "
            "value are classified as membrane."
        )
        paramsLayout.addRow("Membrane Threshold:", self.membraneThresholdSlider)

        self.minSizeSpinBox = qt.QSpinBox()
        self.minSizeSpinBox.minimum = 0
        self.minSizeSpinBox.maximum = 100000
        self.minSizeSpinBox.value = 500
        self.minSizeSpinBox.setToolTip(
            "Minimum segment size in voxels. Segments smaller than this are removed."
        )
        paramsLayout.addRow("Min Segment Size (voxels):", self.minSizeSpinBox)

        self.fillHolesCheckBox = qt.QCheckBox("Fill holes in segments")
        self.fillHolesCheckBox.checked = True
        paramsLayout.addRow(self.fillHolesCheckBox)

        # --- Output section ---
        outputCollapsible = ctk.ctkCollapsibleButton()
        outputCollapsible.text = "Output"
        self.layout.addWidget(outputCollapsible)
        outputLayout = qt.QFormLayout(outputCollapsible)

        self.outputSegmentationSelector = slicer.qMRMLNodeComboBox()
        self.outputSegmentationSelector.nodeTypes = ["vtkMRMLSegmentationNode"]
        self.outputSegmentationSelector.selectNodeUponCreation = True
        self.outputSegmentationSelector.addEnabled = True
        self.outputSegmentationSelector.removeEnabled = True
        self.outputSegmentationSelector.renameEnabled = True
        self.outputSegmentationSelector.noneEnabled = True
        self.outputSegmentationSelector.setMRMLScene(slicer.mrmlScene)
        self.outputSegmentationSelector.setToolTip(
            "Select or create a segmentation node for the output."
        )
        outputLayout.addRow("Output Segmentation:", self.outputSegmentationSelector)

        # --- Run button ---
        self.runButton = qt.QPushButton("Run Segmentation")
        self.runButton.toolTip = "Start the neuron segmentation pipeline."
        self.runButton.enabled = False
        self.layout.addWidget(self.runButton)

        # --- Progress ---
        self.progressBar = qt.QProgressBar()
        self.progressBar.visible = False
        self.layout.addWidget(self.progressBar)

        self.layout.addStretch(1)

        # --- Connections ---
        self.runButton.connect("clicked(bool)", self.onRunButtonClicked)
        self.inputVolumeSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onInputChanged
        )

    def onInputChanged(self, node):
        self.runButton.enabled = node is not None

    def onRunButtonClicked(self):
        inputVolume = self.inputVolumeSelector.currentNode()
        if inputVolume is None:
            slicer.util.errorDisplay("Please select an input EM volume.")
            return

        params = {
            "gaussian_sigma": self.gaussianSigmaSlider.value,
            "membrane_threshold": int(self.membraneThresholdSlider.value),
            "min_segment_size": self.minSizeSpinBox.value,
            "fill_holes": self.fillHolesCheckBox.checked,
        }

        outputSegmentation = self.outputSegmentationSelector.currentNode()
        if outputSegmentation is None:
            outputSegmentation = slicer.mrmlScene.AddNewNodeByClass(
                "vtkMRMLSegmentationNode", "NeuronSegmentation"
            )
            self.outputSegmentationSelector.setCurrentNode(outputSegmentation)

        self.progressBar.visible = True
        self.progressBar.setValue(0)
        self.runButton.enabled = False

        try:
            self.logic.run_segmentation(inputVolume, outputSegmentation, params)
            self.progressBar.setValue(100)
            slicer.util.infoDisplay("Segmentation complete.")
        except Exception as e:
            slicer.util.errorDisplay(f"Segmentation failed: {e}")
            logging.error(f"NeuronSegmenter error: {e}", exc_info=True)
        finally:
            self.runButton.enabled = True

    def cleanup(self):
        pass


class NeuronSegmenterLogic(ScriptedLoadableModuleLogic):
    """Orchestrates the segmentation pipeline by delegating to library classes."""

    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.seg_logic = NeuronSegmentationLogic()
        self.morph_utils = MorphologyUtils()

    def run_segmentation(self, input_volume_node, output_segmentation_node, params):
        """
        Full pipeline: preprocess -> segment -> post-process -> write to Slicer node.
        """
        logging.info("NeuronSegmenter: starting segmentation pipeline")

        import numpy as np

        volume_array = slicer.util.arrayFromVolume(input_volume_node)

        smoothed = self.seg_logic.preprocess(
            volume_array, sigma=params["gaussian_sigma"]
        )

        labels = self.seg_logic.segment_neurons(
            smoothed, membrane_threshold=params["membrane_threshold"]
        )

        labels = self.morph_utils.remove_small_objects(
            labels, min_size=params["min_segment_size"]
        )
        if params["fill_holes"]:
            labels = self.morph_utils.fill_holes(labels)

        self._write_labels_to_segmentation(
            labels, input_volume_node, output_segmentation_node
        )

        logging.info(
            f"NeuronSegmenter: segmentation complete -- "
            f"{len(np.unique(labels)) - 1} neurons found"
        )

    def _write_labels_to_segmentation(
        self, labels, reference_volume, segmentation_node
    ):
        """Convert a numpy label array into a Slicer segmentation node."""
        import numpy as np

        labelmap_node = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLLabelMapVolumeNode", "TempLabelMap"
        )
        slicer.util.updateVolumeFromArray(labelmap_node, labels)

        labelmap_node.SetOrigin(reference_volume.GetOrigin())
        labelmap_node.SetSpacing(reference_volume.GetSpacing())
        directions = vtk.vtkMatrix4x4()
        reference_volume.GetIJKToRASDirectionMatrix(directions)
        labelmap_node.SetIJKToRASDirectionMatrix(directions)

        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
            labelmap_node, segmentation_node
        )

        slicer.mrmlScene.RemoveNode(labelmap_node)
