# Details

# Instructions: to run, navigate to execute_tool.py and run the file

from PySide2.QtCore import * 
from PySide2.QtGui import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from functools import partial
import maya.cmds as cmds
from maya import OpenMayaUI
from pathlib import Path
from shiboken2 import wrapInstance
import os

#keep track of transform settings created by user
class Transform():
    def __init__(self):
        self.radius = 0.0
        self.outer = None
        self.center = None
        self.scatter = None
        self.shape = None
        self.duplicate = False
        self.num_duplicate = 0
        
#show gui window
def showWindow():
    # get this files location so we can find the .ui file in the /ui/ folder alongside it
    UI_FILE = str(Path(__file__).parent.resolve() / "gui.ui")
    loader = QUiLoader()
    file = QFile(UI_FILE)
    file.open(QFile.ReadOnly)
     
    #Get Maya main window to parent gui window to it
    mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)
    ui = loader.load(file, parentWidget=mayaMainWindow)
    file.close()
    
    ui.setParent(mayaMainWindow)
    ui.setWindowFlags(Qt.Window)
    ui.setWindowTitle('Place Around Center Tool')
    ui.setObjectName('Place_Around_Center')
    ui.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

    global folder_path
    folder_path = ''

    def create_ai_standard_surface(material_name):
        # Create a new material
        material = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
        cmds.setAttr(f"{material}.diffuseRoughness", 0.000)
        cmds.setAttr(f'{material}.emission', 1)
        cmds.setAttr(f'{material}.emissionColor', 0, 0, 0, type='double3')
        
        # Create a shading group
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="set")

        # Create a place2dTexture node
        place2d_texture = cmds.shadingNode('place2dTexture', asUtility=True, name='place2dTexture')
        connections = [
            ('coverage', 'coverage'),
            ('translateFrame', 'translateFrame'),
            ('rotateFrame', 'rotateFrame'),
            ('mirrorU', 'mirrorU'),
            ('mirrorV', 'mirrorV'),
            ('stagger', 'stagger'),
            ('wrapU', 'wrapU'),
            ('wrapV', 'wrapV'),
            ('repeatUV', 'repeatUV'),
            ('offset', 'offset'),
            ('rotateUV', 'rotateUV'),
            ('noiseUV', 'noiseUV'),
            ('vertexUvOne', 'vertexUvOne'),
            ('vertexUvTwo', 'vertexUvTwo'),
            ('vertexUvThree', 'vertexUvThree'),
            ('vertexCameraOne', 'vertexCameraOne'),
            ('outUV', 'uvCoord'),
            ('outUvFilterSize', 'uvFilterSize')
        ]

        # Create a file texture node for baseColor
        baseColor_file_node = cmds.shadingNode('file', asTexture=True, name='bigPlantUVs_lambert3_BaseColor.1001.png')
        baseColorFilePath = '/Users/natashadaas/MyPlugins/ShaderPlugin/testFiles/bigPlantTextures/bigPlantUVs_lambert3_BaseColor.1001.png'
        cmds.setAttr(f"{baseColor_file_node}.fileTextureName", baseColorFilePath, type="string")

        # Create a file texture node for Normal
        normal_file_node = cmds.shadingNode('file', asTexture=True, name='bigPlantUVs_lambert3_Normal.1001.png')
        normalFilePath = '/Users/natashadaas/MyPlugins/ShaderPlugin/testFiles/bigPlantTextures/bigPlantUVs_lambert3_Normal.1001.png'
        cmds.setAttr(f"{normal_file_node}.fileTextureName", normalFilePath, type="string")
        cmds.setAttr(f"{normal_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{normal_file_node}.colorSpace', 'Raw', type='string')

        # Create a file texture node for Metalness
        metalness_file_node = cmds.shadingNode('file', asTexture=True, name='bigPlantUVs_lambert3_Metalness.1001.png')
        metalnessFilePath = '/Users/natashadaas/MyPlugins/ShaderPlugin/testFiles/bigPlantTextures/bigPlantUVs_lambert3_Metalness.1001.png'
        cmds.setAttr(f"{metalness_file_node}.fileTextureName", metalnessFilePath, type="string")
        cmds.setAttr(f"{metalness_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{metalness_file_node}.colorSpace', 'Raw', type='string')

        # Create a file texture node for Roughness
        roughness_file_node = cmds.shadingNode('file', asTexture=True, name='bigPlantUVs_lambert3_Roughess.1001.png')
        roughnessFilePath = '/Users/natashadaas/MyPlugins/ShaderPlugin/testFiles/bigPlantTextures/bigPlantUVs_lambert3_Roughness.1001.png'
        cmds.setAttr(f"{roughness_file_node}.fileTextureName", roughnessFilePath, type="string")
        cmds.setAttr(f"{roughness_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{roughness_file_node}.colorSpace', 'Raw', type='string')

        # Connect place2dTexture node to file nodes
        for src, dest in connections:
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{baseColor_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{normal_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{metalness_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{roughness_file_node}.{dest}", force=True)
        
        # Create a multiplyDivide node
        multiply_divide_node = cmds.shadingNode('multiplyDivide', asUtility=True, name='multiplyDivide1')
        cmds.setAttr(f"{multiply_divide_node}.operation", 1) # Set operation as Multiply (1: multiply, 2: divide, 3: power)
        cmds.setAttr(f"{multiply_divide_node}.input2", 1, 1, 1, type="double3")

        # Create a bump2d node
        bump2d_node = cmds.shadingNode('bump2d', asUtility=True, name='bump2d1')

        cmds.connectAttr(material + '.outColor', shading_group + '.surfaceShader', force=True) # Connect material to shading group
        cmds.connectAttr(f"{multiply_divide_node}.output", f"{material}.baseColor", force=True) # Connect multiplyDivide to material
        cmds.connectAttr(f"{baseColor_file_node}.outColor", f"{multiply_divide_node}.input1", force=True) # Connect baseColor file to multiplyDivide
        cmds.connectAttr(f"{bump2d_node}.outNormal", f"{material}.normalCamera", force=True) # Connect bump2d to Normal Camera of material
        cmds.connectAttr(f"{normal_file_node}.outAlpha", f"{bump2d_node}.bumpValue", force=True) # Connect normal file to bump2d
        cmds.connectAttr(f"{metalness_file_node}.outAlpha", f"{material}.metalness", force=True)
        cmds.connectAttr(f"{roughness_file_node}.outAlpha", f"{material}.specularRoughness", force=True)
    
    """
    def get_uv_bounding_box(obj):
        if not cmds.objExists(obj):
            print(f"Object '{obj}' does not exist.")
            return

        # Ensure the object has a shape node
        shape_node = cmds.listRelatives(obj, shapes=True)
        if not shape_node:
            print(f"Object '{obj}' has no shape node.")
            return

        shape_node = shape_node[0]

        # Get the current UV set name
        uv_set = cmds.polyUVSet(shape_node, query=True, currentUVSet=True)[0]

        # Get all UV coordinates of the object
        uv_coords = cmds.polyEditUV(shape_node + '.map[*]', query=True)

        if not uv_coords:
            print(f"No UV coordinates found for object '{obj}'.")
            return

        # Separate UV coordinates into U and V lists
        u_coords = uv_coords[0::2]
        v_coords = uv_coords[1::2]

        # Calculate the bounding box
        u_min = min(u_coords)
        u_max = max(u_coords)
        v_min = min(v_coords)
        v_max = max(v_coords)

        print(f"Bounding box of '{obj}' in UV set '{uv_set}':")
        print(f"U min: {u_min}, U max: {u_max}")
        print(f"V min: {v_min}, V max: {v_max}")
    """

    # open dialog to allow user to choose texture folder
    def showDialog():
        initial_directory = "/Users/natashadaas"  # Replace this with the desired initial directory
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setDirectory(initial_directory)
        dialog.setWindowTitle("Select Folder")

        global folder_path

        # show which filename was selected if a folder was selected
        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
            ui.filename_label.setText(folder_path)
        else:
            ui.filename_label.setText('')

    def create_textures():
        global folder_path
        # get all files in folder_path
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        print(f'Files in {folder_path}:')
        for file in files:
            print(file)

    #apply button clicked
    def apply():
        create_textures()
        #create_ai_standard_surface("MyTestAISSMaterial")
        #get_uv_bounding_box('polySurface51')

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
    ui.select_button.clicked.connect(partial(showDialog))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
