# Details

# Instructions: to run, navigate to execute_tool.py and run the file

#imports
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
import maya.mel as mel
import re

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

    global num_duplicates
    num_duplicates = 0
    global numDistortions
    numDistortions = 0

    global duplicates 
    duplicates = []

    global distort_checkbox
    global distribute_checkbox
    global dd_checkbox
    distort_checkbox = False
    distribute_checkbox = False
    dd_checkbox = False

    global objsToDistribute
    objsToDistribute = []

    ui.distort_amt_input.setValue(0.2)
    global distort_amount
    distort_amount = 0.2

    global x_min_scale
    global y_min_scale
    global z_min_scale
    global x_max_scale
    global y_max_scale
    global z_max_scale
    x_min_scale = 0.7
    y_min_scale = 0.7
    z_min_scale = 0.7
    x_max_scale = 1.0
    y_max_scale = 1.0
    z_max_scale = 1.0
    ui.X_min_scale.setValue(0.7)
    ui.Y_min_scale.setValue(0.7)
    ui.Z_min_scale.setValue(0.7)
    ui.X_max_scale.setValue(1.0)
    ui.Y_max_scale.setValue(1.0)
    ui.Z_max_scale.setValue(1.0)

    #set object to be manupilated
    def getSelectedObjects():
        #cmds.ls returns the list of objects selected
        selected = cmds.ls(sl=True,long=True) or []
        if not selected:
            print("Please select an object.")
        elif len(selected) > 2:
            for i in range(len(selected) - 1):
                print("i: ", selected[i])
                objsToDistribute.append(selected[i])
            t2.center = selected[len(selected) - 1]
            print("t2: ", t2.center)
        elif len(selected) == 1:
            t.center = selected[0]
        else:
            t.center = selected[0] #t.center returns name of object t
            t2.center = selected[1]

    #set variable methods

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

    def set_num_duplicates(num):
        global num_duplicates
        num_duplicates = num

    def set_distort_amount(amt):
        global distort_amount
        distort_amount = amt

    def set_distort_checkbox(c):
        global distort_checkbox
        distort_checkbox = ui.distort_checkbox.checkState()

    def set_distribute_checkbox(c):
        global distribute_checkbox
        distribute_checkbox = ui.distribute_checkbox.checkState()

    def set_dd_checkbox(c):
        global dd_checkbox
        dd_checkbox = ui.dd_checkbox.checkState()

    def set_x_min_scale(scale):
        global x_min_scale
        x_min_scale = scale

    def set_y_min_scale(scale):
        global y_min_scale
        y_min_scale = scale

    def set_z_min_scale(scale):
        global z_min_scale
        z_min_scale = scale

    def set_x_max_scale(scale):
        global x_max_scale
        x_max_scale = scale

    def set_y_max_scale(scale):
        global y_max_scale
        y_max_scale = scale

    def set_z_max_scale(scale):
        global z_max_scale
        z_max_scale = scale

    #general useful methods

    #duplicates t.center and returns the naem of the duplicate
    def duplicateObj():
        global duplicateName
        original_object = t.center  # Assuming "t.center" is the name of your original object
        #cmds.duplicate(original_object)
        duplicate_name_list = cmds.duplicate( t.center, rr=False)
        return duplicate_name_list[0]

    #isolates given object 
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

    def freeze_and_delete_history(obj):
        # Select the object
        cmds.select(obj)

        # Freeze transformations
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

        # Delete history
        cmds.delete(constructionHistory=True)

    # DISTORT FUNCTIONS

    def createDistortion(numVertexIndices):
        randIndex = (int) (random.random() * numVertexIndices) + 1

        global vertexList
        cmds.select(vertexList[randIndex])

        cmds.softSelect(softSelectEnabled=True)  # Enable soft selection
        cmds.softSelect(sse=1,ssd=float(distort_amount),ssc='0,1,2,1,0,2',ssf=float(distort_amount))

        # Get the selected vertices and their surrounding vertices
        selected_vertices = cmds.ls(selection=True, flatten=True)
        cmds.select(selected_vertices)

        global XminDistortion
        global XmaxDistortion
        global YminDistortion
        global YmaxDistortion
        global ZminDistortion
        global ZmaxDistortion
        randDistortionX = random.uniform(XminDistortion,XmaxDistortion)
        randDistortionY = random.uniform(YminDistortion,YmaxDistortion)
        randDistortionZ = random.uniform(ZminDistortion,ZmaxDistortion)

        cmds.move(randDistortionX, randDistortionY, randDistortionZ, relative=True)

    def applyDistortionsToObj(duplicateName):
        global numDistortions
        
        # get number of vertices
        numVertexIndices = cmds.polyEvaluate(duplicateName, vertex=True)

        #create numDistortions number of distortions
        for count in range(numDistortions):
            createDistortion(numVertexIndices)

    def duplicateObjAndApplyDistortions():
        global duplicates
        global duplicateName
        duplicateName = duplicateObj() #duplicate select object
        #freeze_and_delete_history(duplicateName)
        print("duplicateName: ", duplicateName)
        duplicates.append(duplicateName)
     
        cmds.softSelect(softSelectEnabled=False)
        cmds.select(duplicateName) #select duplicated object

        isolateObject(duplicateName) #isolate duplicate

        applyDistortionsToObj(duplicateName) #apply distortions to duplicated object
        
        showAllObjects() #show all objects after distortions complete

        cmds.softSelect(softSelectEnabled=False)

        cmds.select(duplicateName) #select duplicate
        
        global x_min_scale
        global y_min_scale
        global z_min_scale
        global x_max_scale
        global y_max_scale
        global z_max_scale

        randXScale = random.uniform(x_min_scale,x_max_scale) 
        randYScale = random.uniform(y_min_scale,y_max_scale) 
        randZScale = random.uniform(z_min_scale,z_max_scale) 

        cmds.scale(randXScale,randZScale,randZScale)
        
    #object t and t2 should be frozen and their history should be deleted before this
    def duplicateAndDistort():
        global num_duplicates
        global duplicates
        duplicates.append(t.center)

        if (len(duplicates) == 1):
            #do NOT create duplicates - distort object selected
            cmds.softSelect(softSelectEnabled=False)
            cmds.select(t.center) #select duplicated object

            isolateObject(t.center) #isolate duplicate

            applyDistortionsToObj(t.center) #apply distortions to duplicated object
            
            showAllObjects() #show all objects after distortions complete

            cmds.softSelect(softSelectEnabled=False)
        else:
            #create duplicates and distort duplicates
            for i in range(num_duplicates):
                duplicateObjAndApplyDistortions()

        print("length: ", len(duplicates))

    # DISTRIBUTE FUNCTIONS

    # rotates source_object around target_object depending on position of source_object
    def rotate_around_target(source_object, target_object):
        #get the positions of the source and target objects' centers
        source_center = cmds.xform(source_object, q=True, rp=True, ws=True)
        target_center = cmds.xform(target_object, q=True, rp=True, ws=True)

        #galculate the vector from the source object's center to the target object's center
        vector = [target_center[i] - source_center[i] for i in range(3)]
        
        #calculate the rotation angle in the x-z plane using vector math
        rotation_y = math.atan2(vector[0], vector[2]) * (180 / math.pi)

        #rotate the source object around its center in the x-z plane
        cmds.rotate(0, rotation_y, 0, source_object, r=True, os=True)

    #to distribute an object around t2
    #objects do not need to frozen and deleted history for this method
    def distribute(obj):
        cmds.select(obj)
        print("obj: ", obj)

        #get center of cylinder
        bbox = cmds.exactWorldBoundingBox(t2.center) #returns xmin, ymin, zmin, xmax, ymax, zmax
        randX = random.uniform(bbox[0],bbox[3]) 
        randY = random.uniform(bbox[1],bbox[4]) 
        randZ = random.uniform(bbox[2],bbox[5]) 

        pivot_point = cmds.xform(obj, q=True, rp=True, ws=True) #find pivot point of t
        moveCommand = "move -rpr " + str(randX) + " " + str(randY) + " " + str(randZ)
        mel.eval(moveCommand)
        rotate_around_target(obj, t2.center)

    #to distribute all objects in objs[] around t2
    #t's pivot should be at the corner at which user wants it to connect to t2
    def distributeObjs(objs):
        for obj in objs:
            distribute(obj)

    # this gets top most vertices and tip of object 
    # assuming that the object's pivot is at least slightly closer to one side 
    def getFarthestVerticesFromPivot(obj):
        getPivotCommand = "getAttr " + obj + ".scalePivot"
        pivotResult = mel.eval(getPivotCommand) #pivot = (commResult[0],commResult[1],commResult[2])

        #convert mesh vertices to vertex indices
        objVertexIndices = cmds.polyListComponentConversion(obj, toVertex=True)
        objVertexList = cmds.ls(objVertexIndices, flatten=True)

        #find farthest vertex away from pivot
        vIndex = 0
        maxDistance = -1000.0
        maxX = -1000.0
        maxY = -1000.0
        maxZ = -1000.0
        count = 0
        for v in objVertexList:
            vPos =  cmds.pointPosition(v, world=True)
            dist = math.sqrt(((vPos[0]-pivotResult[0])**2)+((vPos[1]-pivotResult[1])**2)+((vPos[2]-pivotResult[2])**2))
            if (dist > maxDistance):
                maxDistance = dist
                maxX = (vPos[0]-pivotResult[0])**2
                maxY = (vPos[1]-pivotResult[1])**2
                maxZ = (vPos[2]-pivotResult[2])**2
                vIndex = count
            count = count + 1

        return vIndex

    def getVerticesSurroundingVertex(obj, vIndex):
        #get pivot
        getPivotCommand = "getAttr " + obj + ".scalePivot"
        pivotResult = mel.eval(getPivotCommand) #pivot = (commResult[0],commResult[1],commResult[2])

        #convert mesh vertices to vertex indices
        objVertexIndices = cmds.polyListComponentConversion(obj, toVertex=True)
        objVertexList = cmds.ls(objVertexIndices, flatten=True)

        #get distance between pivot and farthest vertex
        vPos = cmds.pointPosition(objVertexList[vIndex], world=True)
        maxDist = math.sqrt(((vPos[0]-pivotResult[0])**2)+((vPos[1]-pivotResult[1])**2)+((vPos[2]-pivotResult[2])**2))

        #list of indices surrounding farthest vertex
        surroundingVertices = []

        #add to list
        count = 0
        for v in objVertexList:
            vP =  cmds.pointPosition(v, world=True)
            dist = math.sqrt(((vP[0]-pivotResult[0])**2)+((vP[1]-pivotResult[1])**2)+((vP[2]-pivotResult[2])**2))
            if (abs(maxDist - dist) <= 0.02):
                print("surrounding: ", count)
                surroundingVertices.append(v)
            count = count + 1

        return surroundingVertices

    def snapToVertices(vertices):
        randIndex = (int) (random.random() * len(vertices))
        randVertexPos = cmds.pointPosition(vertices[randIndex], world=True)

        cmds.select(t.center)
        moveCommand = "move -rpr " + str(randVertexPos[0]) + " " + str(randVertexPos[1]) + " " + str(randVertexPos[2])
        mel.eval(moveCommand)

    def distributeInRing():
        farthestVIndex = getFarthestVerticesFromPivot(t2.center)
        surroundingVertices = getVerticesSurroundingVertex(t2.center, farthestVIndex)
        snapToVertices(surroundingVertices)
        rotate_around_target(t.center, t2.center)

    #apply button clicked
    @one_undo
    def apply():
        getSelectedObjects()

        distributeInRing()

        """
        #convert mesh vertices to vertex indices
        vertexIndices = cmds.polyListComponentConversion(t.center, toVertex=True)
        global vertexList
        vertexList = cmds.ls(vertexIndices, flatten=True)
        vertexIndices2 = cmds.polyListComponentConversion(t2.center, toVertex=True)
        global vertexList2
        vertexList2 = cmds.ls(vertexIndices2, flatten=True)

        global distort_checkbox
        global distribute_checkbox
        global dd_checkbox

        global duplicates

        if (distort_checkbox):
            duplicateAndDistort()
        elif (distribute_checkbox):
            distributeObjs(objsToDistribute)
        else:
            duplicateAndDistort()
            distributeObjs(duplicates)
        """

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))

    ui.distort_checkbox.stateChanged.connect(partial(set_distort_checkbox))
    ui.distribute_checkbox.stateChanged.connect(partial(set_distribute_checkbox))
    ui.dd_checkbox.stateChanged.connect(partial(set_dd_checkbox))

    ui.duplicates_input.valueChanged.connect(partial(set_num_duplicates))
    ui.count_input.valueChanged.connect(partial(set_numDistortions))
    ui.X_min_input.valueChanged.connect(partial(set_XminDistortion))
    ui.X_max_input.valueChanged.connect(partial(set_XmaxDistortion))
    ui.Y_min_input.valueChanged.connect(partial(set_YminDistortion))
    ui.Y_max_input.valueChanged.connect(partial(set_YmaxDistortion))
    ui.Z_min_input.valueChanged.connect(partial(set_ZminDistortion))
    ui.Z_max_input.valueChanged.connect(partial(set_ZmaxDistortion))
    ui.distort_amt_input.valueChanged.connect(partial(set_distort_amount))
    ui.X_min_scale.valueChanged.connect(partial(set_x_min_scale))
    ui.Y_min_scale.valueChanged.connect(partial(set_y_min_scale))
    ui.Z_min_scale.valueChanged.connect(partial(set_z_min_scale))
    ui.X_max_scale.valueChanged.connect(partial(set_x_max_scale))
    ui.Y_max_scale.valueChanged.connect(partial(set_y_max_scale))
    ui.Z_max_scale.valueChanged.connect(partial(set_z_max_scale))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()