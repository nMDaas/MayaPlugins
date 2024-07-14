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
import math
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
    ui.setWindowTitle('Shader Plugin')
    ui.setObjectName('Shader plugin')
    ui.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

    global folder_path
    folder_path = ''
    global texture_files
    texture_files = []

    t = Transform()

    def create_ai_standard_surface(material_name, baseColorFile, heightFile, metalnessFile, normalFile, roughnessFile, textureNum):
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
        baseColorNodeName = material_name + "_" + "BaseColor" + "_" + textureNum
        baseColor_file_node = cmds.shadingNode('file', asTexture=True, name=baseColorNodeName)
        baseColorFilePath = baseColorFile
        cmds.setAttr(f"{baseColor_file_node}.fileTextureName", baseColorFilePath, type="string")

        # Create a file texture node for Normal
        normalNodeName = material_name + "_" + "Normal" + "_" + textureNum
        normal_file_node = cmds.shadingNode('file', asTexture=True, name=normalNodeName)
        normalFilePath = normalFile
        cmds.setAttr(f"{normal_file_node}.fileTextureName", normalFilePath, type="string")
        cmds.setAttr(f"{normal_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{normal_file_node}.colorSpace', 'Raw', type='string')

        # Create a file texture node for Metalness
        metalnessNodeName = material_name + "_" + "Metalness" + "_" + textureNum
        metalness_file_node = cmds.shadingNode('file', asTexture=True, name=metalnessNodeName)
        metalnessFilePath = metalnessFile
        cmds.setAttr(f"{metalness_file_node}.fileTextureName", metalnessFilePath, type="string")
        cmds.setAttr(f"{metalness_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{metalness_file_node}.colorSpace', 'Raw', type='string')

        # Create a file texture node for Roughness
        roughnessNodeName = material_name + "_" + "Roughness" + "_" + textureNum
        roughness_file_node = cmds.shadingNode('file', asTexture=True, name=roughnessNodeName)
        roughnessFilePath = roughnessFile
        cmds.setAttr(f"{roughness_file_node}.fileTextureName", roughnessFilePath, type="string")
        cmds.setAttr(f"{roughness_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{roughness_file_node}.colorSpace', 'Raw', type='string')

        # Create a file texture node for Height
        heightNodeName = material_name + "_" + "Height" + "_" + textureNum
        height_file_node = cmds.shadingNode('file', asTexture=True, name=heightNodeName)
        heightFilePath = heightFile
        cmds.setAttr(f"{height_file_node}.fileTextureName", heightFilePath, type="string")
        cmds.setAttr(f"{height_file_node}.alphaIsLuminance", True)
        cmds.setAttr(f'{height_file_node}.colorSpace', 'Raw', type='string')

        # Connect place2dTexture node to file nodes
        for src, dest in connections:
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{baseColor_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{normal_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{metalness_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{roughness_file_node}.{dest}", force=True)
            cmds.connectAttr(f"{place2d_texture}.{src}", f"{height_file_node}.{dest}", force=True)
        
        # Create a multiplyDivide node
        multiply_divide_node = cmds.shadingNode('multiplyDivide', asUtility=True, name='multiplyDivide1')
        cmds.setAttr(f"{multiply_divide_node}.operation", 1) # Set operation as Multiply (1: multiply, 2: divide, 3: power)
        cmds.setAttr(f"{multiply_divide_node}.input2", 1, 1, 1, type="double3")

        # Create a bump2d node
        bump2d_node = cmds.shadingNode('bump2d', asUtility=True, name='bump2d1')
        cmds.setAttr(bump2d_node + '.bumpInterp', 1)

        # Create a displacement shader
        displacement_shader = cmds.shadingNode('displacementShader', asShader=True)

        cmds.connectAttr(material + '.outColor', shading_group + '.surfaceShader', force=True) # Connect material to shading group
        cmds.connectAttr(f"{multiply_divide_node}.output", f"{material}.baseColor", force=True) # Connect multiplyDivide to material
        cmds.connectAttr(f"{baseColor_file_node}.outColor", f"{multiply_divide_node}.input1", force=True) # Connect baseColor file to multiplyDivide
        cmds.connectAttr(f"{bump2d_node}.outNormal", f"{material}.normalCamera", force=True) # Connect bump2d to Normal Camera of material
        cmds.connectAttr(f"{normal_file_node}.outAlpha", f"{bump2d_node}.bumpValue", force=True) # Connect normal file to bump2d
        cmds.connectAttr(f"{metalness_file_node}.outAlpha", f"{material}.metalness", force=True) # Connect metalness file to material
        cmds.connectAttr(f"{roughness_file_node}.outAlpha", f"{material}.specularRoughness", force=True) # Connect roughness file to material
        cmds.connectAttr(f"{height_file_node}.outAlpha", f"{displacement_shader}.displacement", force=True) 
        cmds.connectAttr(f"{displacement_shader}.displacement", f"{shading_group}.displacementShader", force=True)


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

    # clean nodes for this texture
    def cleanNodes(texture_name):
        # get all nodes in the scene
        all_nodes = cmds.ls()

        # Iterate through each node and delete its construction history
        for node in all_nodes:
            if texture_name in node:
                cmds.delete(node)

    def create_textures():
        global folder_path
        global texture_files

        # get all files in folder_path
        texture_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        result = ""

        # organize texture_files by texture numbers
        texture_groups = {}
        for file in texture_files:
            if file.endswith('.png'):
                # get texture number
                length = len(file)
                strTemp = file[length - 8:] # texture number + .png
                textureNum = strTemp[:4]

                if textureNum in texture_groups:
                    # textureNum exists, append file to the existing array
                    texture_groups[textureNum].append(file)
                else:
                    # textureNum does not exist, initialize a new array with the value
                    texture_groups[textureNum] = [file]
        
        # iterate through texture_groups and create textures
        for key,value in texture_groups.items():
            # extract name
            my_string = value[0]
            index = my_string.find('_')
            result = my_string[:index]
            material_name = result + key
            #print("material_name", material_name)

            for file in value:
                if "BaseColor" in file:
                    baseColorFile = file
                if "Height" in file:
                    heightFile = file
                if "Metalness" in file:
                    metalnessFile = file
                if "Normal" in file:
                    normalFile = file
                if "Roughness" in file:
                    roughnessFile = file

            # clean previously created nodes with same name
            cleanNodes(material_name)

            create_ai_standard_surface(material_name, baseColorFile, heightFile, metalnessFile, normalFile, roughnessFile, key)

        return result

    # Set object/group to be textuerd
    def getSelectedObjects():
        selected_objects = cmds.ls(selection=True)
        if len(selected_objects) == 0:
            ui.warnings.setText("Must select an object or group of objects")
        else:
            ui.warnings.setText("")
            return selected_objects[0]
    
    # Get uv bounding box of object based on u_max and v_max value
    def get_uv_bounding_box_from_uv_coords(u_max, v_max):
        v_rounded = math.ceil(v_max)
        #print("v_rounded: ", v_rounded)
        v_value = v_rounded * 1000
        #print("v_value: ", v_value)
        u_value = math.ceil(u_max)
        return v_value + u_value
    
    # Get min and max UV coordinates of object
    def get_uv_bounding_box(obj):
        if not cmds.objExists(obj):
            print(f"Object '{obj}' does not exist.")
            return
        # Get all UV coordinates of the object
        uv_coords = cmds.polyEditUV(obj + '.map[*]', query=True)
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
        #print(f"Bounding box of '{obj}':")
        #print(f"U min: {u_min}, U max: {u_max}")
        #print(f"V min: {v_min}, V max: {v_max}")
        uv_bounding_box = get_uv_bounding_box_from_uv_coords(u_max, v_max)
        return uv_bounding_box
        #print("predicted box: ", uv_bounding_box)
        #print("-----")

    def get_material(mat_name, uv_bounding_box):
        mat_name = mat_name.replace(" ", "")
        uv_bounding_box = str(uv_bounding_box)
        uv_bounding_box = uv_bounding_box.replace(" ", "")
        materials = cmds.ls(materials=True)
        print(materials)
        for mat in materials:
            if mat_name in mat and uv_bounding_box in mat:
                print("found material ", mat_name)
                return mat
        print("texture with *", mat_name, "* + *", uv_bounding_box, "* does not exist")

    # Apply correct texture to object
    def apply_texture_to_mesh(material_name, obj):
        cmds.select(obj, replace=True)
        bounding_box = get_uv_bounding_box(obj)
        material = get_material(material_name,bounding_box)
        
        # Assign the shader to selected object
        cmds.hyperShade(assign=material)

        print("assigning ", material, " to ", obj)
        print("---")

    def apply_textures(selectedObject, mat_name):
        #print(cmds.nodeType(selectedObject))
        if cmds.nodeType(selectedObject) == 'transform':
            #print("group node: ", selectedObject)
            children = cmds.listRelatives(selectedObject, children=True, fullPath=True) or []
            for child in children:
                apply_textures(child, mat_name)
        if cmds.nodeType(selectedObject) == 'mesh':
            apply_texture_to_mesh(mat_name, selectedObject)

    #apply button clicked
    def apply():
        ui.warnings.setStyleSheet("color: red;")

        global folder_path
        selectedObject = getSelectedObjects()
        
        if folder_path == "":
            ui.warnings.setText("Must select a folder path to folder textures")
        else:
            print("trying to do stuff")
            #mat_name = create_textures()
            #apply_textures(selectedObject, mat_name)

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
