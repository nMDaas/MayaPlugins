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

def addInString(a,b,c):
    print("a: ", str(a))
    print("b: ", str(b))
    print("c: ", str(c))
