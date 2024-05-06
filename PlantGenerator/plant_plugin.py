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

    t = Transform() #for leaves (object that will surround t2)
    t2 = Transform() #for stem/branch (object that will be surrounded)

    global X_distort_range
    global Y_distort_range
    global Z_distort_range
    X_distort_range = 0
    Y_distort_range = 0
    Z_distort_range = 0

    global XminDistortion
    global XmaxDistortion
    global YminDistortion
    global YmaxDistortion
    global ZminDistortion
    global ZmaxDistortion
    XminDistortion = 0
    XmaxDistortion = 0
    YminDistortion = 0
    YmaxDistortion = 0
    ZminDistortion = 0
    ZmaxDistortion = 0

    #set object to be manupilated
    def getSelectedObjects():
        #cmds.ls returns the list of objects selected
        selected = cmds.ls(sl=True,long=True) or []
        if not selected:
            print("Please select an object.")
        elif len(selected) > 2:
            print("Please select only two objects.")
        else:
            t.center = selected[0]
            t2.center = selected[1]
            print("t name:",t.center) #t.center returns name of object t
            print("t2 name:", t2.center)

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

    def set_numDistortions(num):
        global numDistortions
        numDistortions = int(num)

    def set_XminDistortion(min):
        global XminDistortion
        XminDistortion = float(min)

    def set_XmaxDistortion(max):
        global XmaxDistortion
        XmaxDistortion = float(max)

    def set_YminDistortion(min):
        global YminDistortion
        YminDistortion = float(min)

    def set_YmaxDistortion(max):
        global YmaxDistortion
        YmaxDistortion = float(max)

    def set_ZminDistortion(min):
        global ZminDistortion
        ZminDistortion = float(min)

    def set_ZmaxDistortion(max):
        global ZmaxDistortion
        ZmaxDistortion = float(max)

    def createDistortion(numVertexIndices):
        randIndex = (int) (random.random() * numVertexIndices) + 1
        print("randIndex: ", randIndex)

        global vertexList
        cmds.select(vertexList[randIndex])

        cmds.softSelect(softSelectEnabled=True)  # Enable soft selection
        cmds.softSelect(sse=1,ssd=2.0,ssc='0,1,2,1,0,2',ssf=2)

        # Get the selected vertices and their surrounding vertices
        selected_vertices = cmds.ls(selection=True, flatten=True)
        cmds.select(selected_vertices)

        global XminDistortion
        global XmaxDistortion
        global YminDistortion
        global YmaxDistortion
        global ZminDistortion
        global ZmaxDistortion
        randDistortionX = (random.random() * XmaxDistortion) + XminDistortion
        randDistortionY = (random.random() * YmaxDistortion) + YminDistortion
        randDistortionZ = (random.random() * ZmaxDistortion) + ZminDistortion

        cmds.move(randDistortionX, randDistortionY, randDistortionZ, relative=True)

    def applyDistortions(duplicateName):
        global numDistortions
        
        # get number of vertices
        numVertexIndices = cmds.polyEvaluate(duplicateName, vertex=True)

        #create numDistortions number of distortions
        for count in range(numDistortions):
            createDistortion(numVertexIndices)

    def duplicateObj():
        global duplicateName
        original_object = t.center  # Assuming "t.center" is the name of your original object
        duplicateName = original_object + "copy"
        #cmds.duplicate(original_object)
        cmds.duplicate( t.center, rr=False, name=duplicateName)

    def isolateObject(objName):
        all_objects = cmds.ls(type='transform', long=True)
        for obj in all_objects:
            if obj != objName:
                cmds.setAttr(obj + ".visibility", 0)  # Hide the object
            else:
                cmds.setAttr(obj + ".visibility", 1)  # Show the specified object

    def showAllObjects():
        all_objects = cmds.ls(type='transform', long=True)
        for obj in all_objects:
            cmds.setAttr(obj + ".visibility", 1)

    def duplicateAndApplyDistortions():
        duplicateObj() #duplicate select object

        global duplicateName
        cmds.softSelect(softSelectEnabled=False)
        cmds.select(duplicateName) #select duplicated object

        isolateObject(duplicateName) #isolate duplicate

        applyDistortions(duplicateName) #apply distortions to duplicated object

        showAllObjects() #show all objects after distortions complete

        cmds.softSelect(softSelectEnabled=False)

        cmds.select(duplicateName) #select duplicate

        #duplicate should be freezed and history should be deleted

    def surround():
        # stem/branch should be  be freezed and history should be deleted before this

        global vertexList2
        minY = 10000.0
        maxY = -10000.0
        centerMin = (0,0,0)
        centerMax = (0,0,0)

        #get stem/branch cylinder (0,minY,0) and (0,maxY,0) where 
        for v in vertexList2:
            vPos = cmds.pointPosition(v, world=True)
            if (vPos[0] == 0) & (vPos[2] == 0): #check if x and z coords == 0
                if float(vPos[1]) < minY:
                    minY = vPos[1]
                if float(vPos[1]) > maxY:
                    maxY = vPos[1]

        #get vertices to which minY and maxY belong
        for v in vertexList2:
            vPos = cmds.pointPosition(v, world=True)
            if (vPos[0] == 0) & (vPos[2] == 0) & (vPos[1] == minY):
                centerMin = v #(0,minY,0)
            if (vPos[0] == 0) & (vPos[2] == 0) & (vPos[1] == maxY):
                centerMax = v #(0,maxY,0)
                
        #get radius of stem/branch
        for v in vertexList2:
            vPos = cmds.pointPosition(v, world=True)
            if vPos[0] != 0 and vPos[2] != 0 and vPos[1] == minY:
                radius = math.sqrt((vPos[0])**2 + vPos[2]**2)
                break

        #get random (x,y,z) points on circle at top of cylinder of stem/branch
        theta = random.uniform(0, 2 * math.pi) #random angle theta between 0 and 2*pi
        randX = radius * math.cos(theta)
        randZ = radius * math.sin(theta)
        vPosMin = cmds.pointPosition(centerMin, world=True)
        vPosMax = cmds.pointPosition(centerMax, world=True)
        randY = random.uniform(vPosMin[1],vPosMax[1]) 
        
        # Move the object to the new position
        cmds.select(t.center)
        cmds.move(randX, randY, randZ, t.center, absolute=True)

    #apply button clicked
    @one_undo
    def apply():
        getSelectedObjects()

        #convert mesh vertices to vertex indices
        vertexIndices = cmds.polyListComponentConversion(t.center, toVertex=True)
        global vertexList
        vertexList = cmds.ls(vertexIndices, flatten=True)
        vertexIndices2 = cmds.polyListComponentConversion(t2.center, toVertex=True)
        global vertexList2
        vertexList2 = cmds.ls(vertexIndices2, flatten=True)

        surround()
        #duplicateAndApplyDistortions()
        

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
    ui.X_input.valueChanged.connect(partial(set_XDistortRange))
    ui.Y_input.valueChanged.connect(partial(set_YDistortRange))
    ui.Z_input.valueChanged.connect(partial(set_ZDistortRange))
    ui.count_input.valueChanged.connect(partial(set_numDistortions))
    ui.X_min_input.valueChanged.connect(partial(set_XminDistortion))
    ui.X_max_input.valueChanged.connect(partial(set_XmaxDistortion))
    ui.Y_min_input.valueChanged.connect(partial(set_YminDistortion))
    ui.Y_max_input.valueChanged.connect(partial(set_YmaxDistortion))
    ui.Z_min_input.valueChanged.connect(partial(set_ZminDistortion))
    ui.Z_max_input.valueChanged.connect(partial(set_ZmaxDistortion))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
