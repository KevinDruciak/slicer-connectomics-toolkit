cmake_minimum_required(VERSION 3.16.3...3.27 FATAL_ERROR)

project(NeuronSegmenter)

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

set(MODULE_NAME NeuronSegmenter)

set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_NAME}Lib/__init__.py
  ${MODULE_NAME}Lib/SegmentationLogic.py
  ${MODULE_NAME}Lib/MorphologyUtils.py
)

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
)

slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
)

if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
