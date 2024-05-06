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

    t = Transform()

    global X_distort_range
    global Y_distort_range
    global Z_distort_range
    X_distort_range = 0
    Y_distort_range = 0
    Z_distort_range = 0

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

    #manupilates vertices of object selected in X axis
    def distortVerticesInX():
        global X_distort_range
        global vertexList

        count = 0

        # Iterate over each vertex and get its position
        for vertex in vertexList:
            #get random distort amount
            randXDistort = random.random() * X_distort_range
            #get vertex name
            vertexName = t.center + ".vtx[" + str(count) + "]"
            #transform vertex in x
            vertexPosition = cmds.pointPosition(vertex, world=True)
            cmds.xform(vertexName,worldSpace=True, translation=(vertexPosition[0] + randXDistort,vertexPosition[1],vertexPosition[2]))
            #increment count
            count = count + 1

    #manupilates vertices of object selected in Y axis
    def distortVerticesInY():
        global Y_distort_range
        global vertexList

        count = 0

        # Iterate over each vertex and get its position
        for vertex in vertexList:
            #get random distort amount
            randYDistort = random.random() * Y_distort_range
            #get vertex name
            vertexName = t.center + ".vtx[" + str(count) + "]"
            #transform vertex in x
            vertexPosition = cmds.pointPosition(vertex, world=True)
            cmds.xform(vertexName,worldSpace=True, translation=(vertexPosition[0],vertexPosition[1] + randYDistort,vertexPosition[2]))
            #increment count
            count = count + 1

    #manupilates vertices of object selected in Z axis
    def distortVerticesInZ():
        global Z_distort_range
        global vertexList

        count = 0

        # Iterate over each vertex and get its position
        for vertex in vertexList:
            #get random distort amount
            randZDistort = random.random() * Z_distort_range
            #get vertex name
            vertexName = t.center + ".vtx[" + str(count) + "]"
            #transform vertex in x
            vertexPosition = cmds.pointPosition(vertex, world=True)
            cmds.xform(vertexName,worldSpace=True, translation=(vertexPosition[0],vertexPosition[1],vertexPosition[2] + randZDistort))
            #increment count
            count = count + 1

    def set_XDistortRange(xRange):
        global X_distort_range
        X_distort_range = float(xRange)

    def set_YDistortRange(yRange):
        global Y_distort_range
        Y_distort_range = float(yRange)

    def set_ZDistortRange(zRange):
        global Z_distort_range
        Z_distort_range = float(zRange)

    def duplicateObj():
        cmds.duplicate( t.center, rr=True ) #what does rr=True do?

    def getSurroundingVertices():
        global vertexList

        cmds.select(vertexList[841])

        cmds.softSelect(softSelectEnabled=True)  # Enable soft selection
        cmds.softSelect(sse=1,ssd=2.0,ssc='0,1,2,1,0,2',ssf=2)

        # Get the selected vertices and their surrounding vertices
        selected_vertices = cmds.ls(selection=True, flatten=True)
        cmds.select(selected_vertices)

        cmds.move(0.0, 1.0, 0.0, relative=True)

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

        #duplicateObj()
        
        #convert mesh vertices to vertex indices
        vertexIndices = cmds.polyListComponentConversion(t.center, toVertex=True)
        global vertexList
        vertexList = cmds.ls(vertexIndices, flatten=True)

        getSurroundingVertices()
        
        #distortVerticesInX()
        #distortVerticesInY()
        #distortVerticesInZ()
        

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
    ui.X_input.valueChanged.connect(partial(set_XDistortRange))
    ui.Y_input.valueChanged.connect(partial(set_YDistortRange))
    ui.Z_input.valueChanged.connect(partial(set_ZDistortRange))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
