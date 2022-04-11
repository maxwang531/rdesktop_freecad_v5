import sys

# Env import
import numpy
from gym import Env
from gym import spaces, core, utils ,logger
from gym.utils import seeding
import numpy as np
import pandas as pd
import random
import math
from math import pi, sin, cos
import csv
from time import sleep

#Sys Path
BINVOXPATH="/config/mnt/rl_demo/utils"
#Sys import
import os
import sys
sys.path.append(BINVOXPATH)

import binvox_rw
import Mesh

#FreeCAD import
import FreeCAD as App
import FreeCADGui as Gui
import setuptools

from FreeCAD import Base, Rotation, Vector
import Part
import Path
import Draft
from PathScripts import PathJob
from PathScripts import PathJobGui

from PathScripts import PathProfile
from PathScripts import PathAdaptive
from PathScripts import PathPocket
from PathScripts import PathSurface

import PathScripts.PathDressupDogbone as PathDressupDogbone
import PathScripts.PathDressupHoldingTags as PathDressupHoldingTags

from PathScripts import PathGeom
from PathScripts import PathPostProcessor
from PathScripts import PathUtil
from PathScripts import PathSimulatorGui as a

from PathScripts import PathToolBit
from PathScripts import PathToolController

# import Stable-Baselines3 für Reinceforment Learning
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecFrameStack , SubprocVecEnv
from stable_baselines3.common.vec_env.dummy_vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_checker import  check_env

'''Datie-Information'''
filepath = '/config/eingabe_model/model.FCStd'
file_name_1 = 'model'
file_name_2 = "model"
file_name_3 = 'Solid'
operation_file = '/config/ausgabe_ngc/operation_parameter.csv'

'''Werkzeug-Information'''
toolpath1 =  "/usr/lib/freecad/Mod/Path/Tools/Bit/317mm_Endmill.fctb"
toolpath2 =  "/usr/lib/freecad/Mod/Path/Tools/Bit/317mm_Endmill.fctb"

''' Die Ausgabe : die Verarbeitungsdaten und die G-Code.'''
csv_file = '/config/ausgabe_ngc/operation_parameter.csv'
gcodePath_surface = '/config/ausgabe_ngc/txt/surface_operation.txt'
gcodePath_surface_neu = '/config/ausgabe_ngc/neu_txt/surface_operation_neu.txt'

''' Datei öffnen (CAD-Modell)'''
DOC=App.openDocument(filepath)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
Part1 = DOC.getObject(file_name_3)

''' Job Erstellung'''
Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job', [Part1], None)
job.ViewObject.Proxy = PathJobGui.ViewProvider(job.ViewObject)
stock = job.Stock
stock.setExpression('ExtXneg',None)
stock.ExtXneg = 0.00
stock.setExpression('ExtXpos',None)
stock.ExtXpos = 0.00
stock.setExpression('ExtYneg',None)
stock.ExtYneg = 0.00
stock.setExpression('ExtYpos',None)
stock.ExtYpos = 0.00
stock.setExpression('ExtZneg',None)
stock.ExtZneg = 0.00
stock.setExpression('ExtZpos',None)
stock.ExtZpos = 0.00

# Clone Select
Part2 = DOC.getObject('Clone')

'''Operation Definition'''
#Werkzeug
def werkzeug(toolpath,name2,horizrapid = "15mm/s",vertrapid = "2mm/s",):
    name1 = PathToolBit.Declaration(toolpath)

    tool = PathToolController.Create(name2)
    tool.setExpression('HorizRapid', None)
    tool.HorizRapid = horizrapid
    tool.setExpression('VertRapid', None)
    tool.VertRapid = vertrapid

    name3 = tool.Tool
    name3.Label = name1['name']
    name3.BitShape = name1['shape']
    name3.CuttingEdgeHeight = name1['parameter']['CuttingEdgeHeight']
    name3.Diameter = name1['parameter']['Diameter']
    name3.Length = name1['parameter']['Length']
    name3.ShankDiameter = name1['parameter']['ShankDiameter']
    name3.recompute()
    name3.ViewObject.Visibility = True
    name3.recompute()
    return name3.Diameter
#3D Surface Operation (Freiformoberflächeauswählen)
def surface(facName,werkzeugname,
            boundaryadjustment , cut_pattern_zahl = 2, layer_mode_zahl = 0,
            stepover = 10, depthoffset = 0,
            circular_use_G2_G3_bool = 0, boundary_enforcement_bool = 0,
            name = 0):
    sur_face = PathSurface.Create('Surface%d'%(name))

    sur_face.Base = (Part2, facName)

    cut_pattern = ['Circular','CircularZigZag','Line','Offset','Spiral','ZigZag']
    sur_face.CutPattern = cut_pattern[cut_pattern_zahl]

    layer_mode = ['Single-pass','Multi-pass']
    sur_face.LayerMode = layer_mode[layer_mode_zahl]

    sur_face.setExpression('StepOver', None)
    sur_face.StepOver = stepover

    sur_face.setExpression('DepthOffset', None)
    sur_face.DepthOffset = depthoffset

    circular_use_G2_G3 = ['true', '']
    sur_face.CircularUseG2G3 = bool(circular_use_G2_G3[circular_use_G2_G3_bool])

    boundary_enforcement = ['true','']
    sur_face.BoundaryEnforcement = bool(boundary_enforcement[boundary_enforcement_bool])

    sur_face.setExpression('BoundaryAdjustment', None)
    sur_face.BoundaryAdjustment = boundaryadjustment

    Gui.Selection.addSelection(file_name_1, 'Surface%d' % (name))
    App.getDocument(file_name_1).getObject('Surface%d' % (name)).ToolController = App.getDocument(
        file_name_1).getObject(werkzeugname)

    DOC.recompute()

#Werkzeugaufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit002').ShapeName = "endmill"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
werkzeugdiameter = [tool1_diameter,tool2_diameter]

#3D Werkzeugwegparameter lesen (von csv-Datei)
operation = pd.read_csv(operation_file)
auswahl_werkzeug = operation.iloc[0,1]
auswahl_werkzeug_diamenter = operation.iloc[1,1]
auswhal_cutpattern = int(operation.iloc[2,1])
auswahl_stepover = int(operation.iloc[3,1])

#3D Oberflächenauswahl
obj = App.ActiveDocument.getObject('Solid')
xmin = obj.Shape.BoundBox.XMin
ymin = obj.Shape.BoundBox.YMin
zmin = obj.Shape.BoundBox.ZMin
xmax = obj.Shape.BoundBox.XMax
ymax = obj.Shape.BoundBox.YMax
zmax = obj.Shape.BoundBox.ZMax
modellange = xmax-xmin
face_anzahl_list = obj.Shape.Faces #Information von Face von Modell
face_type_list = [] #Information von Facetype (Oberflächen existieren nur in wenigen Fällen)
face_volume_list = [] # Das Volumen der Oberfläche ist im Allgemeinen größer oder kleiner als 0
face_axis_list = [] # Nur die obere Fläche kann bearbeitet werden
face_zmin_list = []
face_zmax_list = []
for i in range(0,len(face_anzahl_list)):
    face_type = App.ActiveDocument.Solid.Shape.Faces[i].Surface.TypeId
    face_volume = App.ActiveDocument.Solid.Shape.Faces[i].Volume
    face_axis = App.ActiveDocument.Solid.Shape.Faces[i].Surface.Axis
    face_zmin = App.ActiveDocument.Solid.Shape.Faces[i].BoundBox.ZMin
    face_zmax = App.ActiveDocument.Solid.Shape.Faces[i].BoundBox.ZMax
    face_type_list.append(face_type)
    face_volume_list.append(face_volume)
    face_axis_list.append(list(face_axis))
    face_zmin_list.append(face_zmin)
    face_zmax_list.append(face_zmax)

select_face_id = []
select_face = [] # Alle zu bearbeitenden Freiformflächenmerkmale. (Face id)
for i in range(0,len(face_anzahl_list)):
    if face_type_list[i] == 'Part::GeomBSplineSurface' and face_volume_list[i] > 1:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] == 'Part::GeomBSplineSurface' and face_volume_list[i] < -1:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] == 'Part::GeomCylinder' and face_volume_list[i] > 1 and face_axis_list[i] == [-1.0,0.0,0.0]:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] == 'Part::GeomCylinder' and face_volume_list[i] > 1 and face_axis_list[i] == [1.0,0.0,0.0]:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] == 'Part::GeomCylinder' and face_volume_list[i] < -1 and face_axis_list[i] == [-1.0,0.0,0.0]:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] == 'Part::GeomCylinder' and face_volume_list[i] < -1 and face_axis_list[i] == [1.0,0.0,0.0]:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] ==  'Part::GeomSphere' and face_volume_list[i] > 1:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_type_list[i] ==  'Part::GeomSphere' and face_volume_list[i] < -1:
        select_face_id.append(i+1)
        select_face.append('Face{:d}'.format(i+1))
    if face_zmax_list[i] == face_zmin_list[i] == zmin+modellange:
        select_face_id.append(i + 1)
        select_face.append('Face{:d}'.format(i + 1))

#werkzeugweg
surface(select_face,auswahl_werkzeug,auswahl_werkzeug_diamenter,cut_pattern_zahl=auswhal_cutpattern,stepover=auswahl_stepover,depthoffset=0,name = 0)
print("--- done ---")

job.PostProcessorOutputFile = gcodePath_surface
job.PostProcessor = 'linuxcnc'
job.PostProcessorArgs = '--no-show-editor'
postlist = []
currTool = None
for obj in job.Operations.Group:
    print( obj.Name)
    tc = PathUtil.toolControllerForOp(obj)
    if tc is not None:
        if tc.ToolNumber != currTool:
            postlist.append(tc)
            currTool = tc.ToolNumber
    postlist.append(obj)

post = PathPostProcessor.PostProcessor.load(job.PostProcessor)
gcode = post.export(postlist, gcodePath_surface, job.PostProcessorArgs)
DOC.recompute()
print("--- g-code export finished ---")

'''Bearbeitung der Ausgabe von 3D-Features.'''
data_surface = []
for line in open('/config/ausgabe_ngc/txt/surface_operation.txt',"r"):
    data_surface.append(line)
del data_surface[0:13]
del data_surface[len(data_surface) - 3:len(data_surface)]
data_surface.insert(0,'G17 G54 G40 G49 G80 G90\n')
data_surface.insert(1,'G21\n')
data_surface.insert(2,'M5\n')
data_surface.insert(3,'M6 T1 \n')
data_surface.insert(4,'G43 H1  \n')
data_surface.insert(5,'M3 S10000 \n')
data_surface.insert(6,'F2000 \n')
data_surface.insert(7, 'G0 A90\n')
data_surface.insert(len(data_surface)+1,'M05\n')
data_surface.insert(len(data_surface)+2,'G17 G54 G90 G80 G40\n')
data_surface.insert(len(data_surface)+2,'M2\n')
f=open('/config/ausgabe_ngc/neu_txt/surface_operation_neu.txt',"w")
for line in data_surface:
    f.write(line+'\n')
f.close()
f=open('/config/ausgabe_ngc/surface_operation_neu.ngc',"w")
for line in data_surface:
    f.write(line+'\n')
f.close()

'''2D+3D Werkzeugweg (Kombinieren)'''
data_3D = []
for line in open('/config/ausgabe_ngc/neu_txt/surface_operation_neu.txt',"r"):
    data_3D.append(line)
del data_3D[len(data_3D)-7:len(data_3D)]
data_2D = []
for line in open('/config/ausgabe_ngc/neu_txt/operation_neu.txt',"r"):
    data_2D.append(line)
del data_2D[0:14]

data_gesamt = data_3D+data_2D
f=open('/config/ausgabe_ngc/neu_txt/3D+2D.txt',"w")
for line in data_gesamt:
    f.write(line+'\n')
f.close()
f=open('/config/ausgabe_ngc/3D+2D.ngc',"w")
for line in data_gesamt:
    f.write(line+'\n')
f.close()

Gui.doCommand('exit()')
