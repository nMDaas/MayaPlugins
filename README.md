# Plant Generator Plugin for Maya
I developed this tool to eliminate inefficient processes in plant modeling such as duplicating plant parts, modifying plants parts individually and correctly placing plant parts so they are connected to the rest of the plant. 

## How To Use
* Download folder for the plugin you want to use
* In the execute.py file, update the line with "folder =" to be the path to the plugin folder on your computer
* Open the "execute_tool.py" file in the Maya script editor
* Run the script

## GUI Design and Tool Functionality
<img src="https://github.com/nMDaas/MayaPlugins/blob/main/images/GUI.png" alt="drawing" width="500"/>

This tool allows several features to streamline the plant modeling process:
- **Tool Options:**
     - **Distort:**
       - Distorts a plant plant or creates distorted duplicates of a plant part based on ***Number of Duplicates*** value
       - Needs only one object
     - **Distribute:**
       - Distributes a plant part or multiple plant parts (via shift select) around the bounding box of another object based on arrangement chosen in ***Distribute Options***
       - Needs two objects (object(s) to distribute and object to distribute around)
     - **Both:**
       - Distorts object or creates distorted duplicates of object based on ***Distortions*** parameters and distributes around the other object based on ***Distribute Options*** chosen
       - Needs two objects (object(s) to distribute and object to distribute around)
     - **Tilt:** Tilts one or more object in a specific direction based on the ***Tilt*** section parameters
 - **Number of Duplicates:**
    - Sets number of duplicates of the plant part to be made
    - Setting it to 0 will create no duplicates even if ***Distortion*** >> ***Count*** > 1 (it will just distort the current object)
- **Distortions:**
  - **Count:**
    - Number of distortions to be created
    - For each distortion, a random value between ***X Min*** and ***X Max***, ***Y Min*** and ***Y Max*** and ***Z Min*** and ***Z Max*** is chosen _(I recommend testing with min and max values between 0.0 and 1.0)_
  - **Amount:** Influence of the distortion _(I recommend something like 0.2)_
 - **Min Scale** and **Max Scale:** set range to randomize plant part sizes (resulting size = original size * randomized scale)
 - **Distribute Options:** if selected, object(s) are distributed at the top of the object instead of around the bounding box of the object

## Tool Demo:  

### Demo #1: https://youtu.be/xSYAs8dseuE
* Plant part _(leaf,stem)_ duplication + modification
* Distribution of multiple plant parts _(stems)_ throughout top of object _(pot)_
* Distribution of single plant part _(leaf)_ at top of object _(stem)_
<img src="https://github.com/nMDaas/PlantGeneratorPluginMaya/blob/main/images/plant1.jpg" alt="drawing" width="500"/>

#### Demo #2: https://youtu.be/Inyv8dLwAZ8
* Creation of branch system around a stem
* Plant part tilting
<img src="https://github.com/nMDaas/PlantGeneratorPluginMaya/blob/main/images/plant2.jpg" alt="drawing" width="500"/>

#### More Results From This Tool:
<img src="https://github.com/nMDaas/PlantGeneratorPluginMaya/blob/main/images/plant3.jpg" alt="drawing" width="500"/>
<img src="https://github.com/nMDaas/PlantGeneratorPluginMaya/blob/main/images/render3.jpg" alt="drawing" width="500"/>
<img src="https://github.com/nMDaas/PlantGeneratorPluginMaya/blob/main/images/plantGen.jpg" alt="drawing" width="500"/>
