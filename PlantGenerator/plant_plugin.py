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

    #function for the clicked center object button
    def clicked_center_button():
        #get selected object(s)
        selected = cmds.ls(sl=True,long=True) or []
        if not(len(selected) == 1):
            print("Please set center to be exactly 1 selected object.")
        else: 
            t.center = selected[0]
        #Change location of locator to be at center object's pivot position
        x = cmds.getAttr(t.center + ".translateX")
        y = cmds.getAttr(t.center + ".translateY")
        z = cmds.getAttr(t.center + ".translateZ")
        #change ui text
        ui.center_objs.setText(t.center[1:])
    
    #apply button clicked
    def apply():
        #User error handling
        if t.center == None:
            ui.warnings.setText("<font color='red'>Warning:Please set a center object.</font>")
            return
        else: # all proper fields have been set
            ui.warnings.setText("")

        cmds.move( 5, 5, 5, 'pCube2', absolute=True )

#Close dialog
    def close():
        ui.done(0)

    #connect buttons to functions
    ui.center_button.clicked.connect(partial(clicked_center_button))
    ui.apply_button.clicked.connect(partial(apply))
    ui.close_button.clicked.connect(partial(close))
     
    # show the QT ui
    ui.show()
    return ui

if __name__ == "__main__":
    window=showWindow()
