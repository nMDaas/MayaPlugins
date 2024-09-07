# Maya tool which allows users to easily and quickly place objects in/around another object 
# with a set radius and many other customizable parameters.

# Instructions: Make any changes to the path desired and run this file.

import sys

#SET THIS FOLDER to the parent folder that you've downloaded the repository to
#or ensure that the parent folder is added to your PYTHONPATH
folder = '/Users/natashadaas/PlantGeneratorPluginMaya'

#check if folder is part of PYTHONPATH and if not, add it
if folder not in sys.path:
    sys.path.append(folder)

if 'PlantGenerator' in sys.modules:
    del sys.modules['PlantGenerator']
if 'PlantGenerator.plant_plugin' in sys.modules:
    del sys.modules['PlantGenerator.plant_plugin']
import PlantGenerator.plant_plugin
if 'PlantGenerator.distort_utils' in sys.modules:
    del sys.modules['PlantGenerator.distort_utils']
import PlantGenerator.distort_utils

window = PlantGenerator.plant_plugin.showWindow()