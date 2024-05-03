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
from functools import wraps

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

def one_undo(func):
    """
    Decorator - guarantee close chunk.
    type: (function) -> function
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            cmds.undoInfo(closeChunk=True)
    return wrap
        
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
    ui.setWindowTitle('Plant Generator Tool')
    ui.setObjectName('Plant_Generator')
    ui.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

    ui.horizontal_input.setEnabled(False)
    ui.vertical_input.setEnabled(False)

    t = Transform()

    global applyHorizontalDistort
    applyHorizontalDistort = False
    global applyVerticalDistort
    applyVerticalDistort = False

    #set object to be manupilated
    def setSelectedObject():
        #cmds.ls returns the list of objects selected
        selected = cmds.ls(sl=True,long=True) or []
        if not selected:
            print("Please select an object.")
        elif len(selected) > 1:
            print("Please select only one object.")
        else:
            t.center = selected[0]
            print("t name:",t.center) #t.center returns name of object t
            ui.center_objs.setText(t.center[1:])

    #toggle applyHorizontalDistort
    def set_applyHorizontalDistort():
        global applyHorizontalDistort 
        applyHorizontalDistort = ui.horizontal_checkbox.checkState()
        if applyHorizontalDistort:
            ui.horizontal_input.setEnabled(True)
        else:
            ui.horizontal_input.setEnabled(False)

    #toggle applyVerticalDistort
    def set_applyVerticalDistort():
        global applyVerticalDistort 
        applyVerticalDistort = ui.vertical_checkbox.checkState()
        if applyVerticalDistort:
            ui.vertical_input.setEnabled(True)
        else:
            ui.vertical_input.setEnabled(False)

    #manupilates vertices of object selected horizontally
    def distortVerticesHorizontally():
        print("distortVerticesHorizontally called")
        global horizontal_distort_range
        global vertexList

        count = 0

        # Iterate over each vertex and get its position
        for vertex in vertexList:
            #get random distort amount
            randHorizontalDistort = random.random() * horizontal_distort_range
            #get vertex name
            vertexName = t.center + ".vtx[" + str(count) + "]"
            #transform vertex horizontally
            vertexPosition = cmds.pointPosition(vertex, world=True)
            cmds.xform(vertexName,worldSpace=True, translation=(vertexPosition[0] + randHorizontalDistort,vertexPosition[1],vertexPosition[2]))
            #increment count
            count = count + 1

    #manupilates vertices of object selected vertically
    def distortVerticesVertically():
        print("distortVerticesVertically called")
        global vertical_distort_range
        global vertexList

        count = 0

        # Iterate over each vertex and get its position
        for vertex in vertexList:
            #get random distort amount
            randVerticalDistort = random.random() * vertical_distort_range
            #get vertex name
            vertexName = t.center + ".vtx[" + str(count) + "]"
            #transform vertex horizontally
            vertexPosition = cmds.pointPosition(vertex, world=True)
            cmds.xform(vertexName,worldSpace=True, translation=(vertexPosition[0],vertexPosition[1] + randVerticalDistort,vertexPosition[2]))
            #increment count
            count = count + 1

    def set_horizontalDistortRange(hRange):
        global horizontal_distort_range
        horizontal_distort_range = float(hRange)

    def set_verticalDistortRange(vRange):
        global vertical_distort_range
        vertical_distort_range = float(vRange)

    #apply button clicked
    @one_undo
    def apply():
        setSelectedObject()

        #User error handling
        if t.center == None:
            ui.warnings.setText("<font color='red'>Warning:Please set a center object.</font>")
            return
        else: # all proper fields have been set
            ui.warnings.setText("")
        
        # Convert mesh vertices to vertex indices
        vertexIndices = cmds.polyListComponentConversion(t.center, toVertex=True)
        global vertexList
        vertexList = cmds.ls(vertexIndices, flatten=True)

        global applyHorizontalDistort
        global applyVerticalDistort

        print('applyHorizontalDistort: ', applyHorizontalDistort)
        print('applyVerticalDistort: ', applyVerticalDistort)
        
        if applyHorizontalDistort:
            distortVerticesHorizontally()

        if applyVerticalDistort:
            distortVerticesVertically()
        

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
    ui.horizontal_checkbox.clicked.connect(partial(set_applyHorizontalDistort))
    ui.vertical_checkbox.clicked.connect(partial(set_applyVerticalDistort))
    ui.horizontal_input.valueChanged.connect(partial(set_horizontalDistortRange))
    ui.vertical_input.valueChanged.connect(partial(set_verticalDistortRange))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
