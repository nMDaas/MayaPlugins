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
import math
from shiboken2 import wrapInstance
from random import randrange
import random

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

    t = Transform()

    def create_ai_standard_surface(material_name):
        # Create a new material
        material = cmds.shadingNode('aiStandardSurface', asShader=True, name=material_name)
        cmds.setAttr(f"{material}.diffuseRoughness", 0.000)
        
        # Create a shading group
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="set")

        # Create a place2dTexture node
        place2d_texture = cmds.shadingNode('place2dTexture', asUtility=True, name='myPlace2dTexture')
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

        for src, dest in connections:
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{baseColor_file_node}.{dest}", force=True)
        
        # Create a multiplyDivide node
        multiply_divide_node = cmds.shadingNode('multiplyDivide', asUtility=True, name='multiplyDivide1')
        cmds.setAttr(f"{multiply_divide_node}.operation", 1) # Set operation as Multiply (1: multiply, 2: divide, 3: power)
        cmds.setAttr(f"{multiply_divide_node}.input2", 1, 1, 1, type="double3")

        cmds.connectAttr(material + '.outColor', shading_group + '.surfaceShader', force=True) # Connect material to shading group
        cmds.connectAttr(f"{multiply_divide_node}.output", f"{material}.baseColor", force=True) # Connect multiplyDivide to material
        cmds.connectAttr(f"{baseColor_file_node}.outColor", f"{multiply_divide_node}.input1", force=True)
    
    #apply button clicked
    def apply():
        create_ai_standard_surface("MyTestAISSMaterial")

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
