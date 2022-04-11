
# import sys
import csv
from typing import List
import numpy as np
import pandas as pd
from pandas import DataFrame, Series

#FreeCAD import
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Base, Rotation, Vector
import Part
import Path
import Draft
from PathScripts import PathJob
from PathScripts import PathJobGui
from PathScripts import PathAdaptive
import PathScripts.PathDressupDogbone as PathDressupDogbone
import PathScripts.PathDressupHoldingTags as PathDressupHoldingTags
from PathScripts import PathGeom
from PathScripts import PathPostProcessor
from PathScripts import PathUtil
from PathScripts import PathToolBit
from PathScripts import PathToolController


# Informationspfad eingeben
SsdNet_filepath = '/config/eingabe_model/csv_file/ssd_information.csv' #Information von SsdNet
result_filepath = '/config/eingabe_model/csv_file/result_information.csv' #Information von csv_bearbeitung.py
filepath = '/config/eingabe_model/bool_model/Common.FCStd' # Model nach boolschen Operation
filepath_original = '/config/eingabe_model/model.FCStd' #Model vor boolschen Operation
file_name_1 = 'model'
file_name_2 = 'Solid'
toolpath1 = "/usr/lib/freecad/Mod/Path/Tools/Bit/317mm_Endmill.fctb" # Verwendete Werkzeug
toolpath2 = "/usr/lib/freecad/Mod/Path/Tools/Bit/157mm_Ball_End.fctb" #Verwendete Werkzeug
gcodePath_top = '/config/ausgabe_ngc/txt/top_operation.txt' # g-code Ausgabenspfad
gcodePath_site1 = '/config/ausgabe_ngc/txt/site1_operation.txt'
gcodePath_site2 = '/config/ausgabe_ngc/txt/site2_operation.txt'
gcodePath_site3 = '/config/ausgabe_ngc/txt/site3_operation.txt'
gcodePath_site4 = '/config/ausgabe_ngc/txt/site4_operation.txt'

'''Das Originalmodell öffnen und die Seitenlänge des Modells berechnen.'''
DOC=App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
obj = App.ActiveDocument.getObject('Solid')
xmin = obj.Shape.BoundBox.XMin
ymin = obj.Shape.BoundBox.YMin
zmin = obj.Shape.BoundBox.ZMin
xmax = obj.Shape.BoundBox.XMax
ymax = obj.Shape.BoundBox.YMax
zmax = obj.Shape.BoundBox.ZMax
modell_länge = xmax-xmin
App.closeDocument("model") # Model schließen

'''Die von SsdNet ausgegebene csv-Datei lesen'''
ssdnet_Daten = pd.read_csv(SsdNet_filepath) # DataFrame von SsdNet
ssdnet_Daten_zeile = ssdnet_Daten.shape[0] # Die Anzahl der Merkmale, die das Modell enthält.
ssdnet_list = ssdnet_Daten.values.tolist() # DataFrame zu List
ssdnet_array = np.array(ssdnet_list) # List zu Array
such_element_1 = 0 # Der erste spezielle Wert ist 0.
such_element_2 = modell_länge # Der zweite besondere Wert ist die Seitenlänge des Modells.
ssdnet_array_index_such_element_1 = np.where(ssdnet_array == such_element_1)
ssdnet_array_index_such_element_1_matrix = np.dstack((ssdnet_array_index_such_element_1[0], ssdnet_array_index_such_element_1[1])).squeeze()
ssdnet_array_index_such_element_2 = np.where(ssdnet_array == such_element_2)
ssdnet_array_index_such_element_2_matrix = np.dstack((ssdnet_array_index_such_element_2[0], ssdnet_array_index_such_element_2[1])).squeeze()
ssdnet_list_index_such_element_1_matrix = ssdnet_array_index_such_element_1_matrix.tolist()
ssdnet_list_index_such_element_2_matrix = ssdnet_array_index_such_element_2_matrix.tolist()
#ssdnet_list_index_such_element_1_matrix =[[0, 0], [0, 2], [2, 1], [4, 1]] ist ein Beispiel，[4,1]bedeutet, dass die vierte Zeile und erste Spalte der Liste "0" ist.
#ssdnet_list_index_such_element_2_matrix =[[1, 6], [2, 6], [3, 6], [5, 4]] ist ein Beispiel，[5,4]bedeutet, dass die fünfte Zeile und vierte Spalte der Liste "Modellänge" ist.

'''Erstellen eines Wörterbuchs mit der Anzahl der Zeilen als Schlüssel'''
# Schritt1: Erstellen einer Liste von Zeilenzählungen (ssdnet_Daten_zeile == 1)
if ssdnet_Daten_zeile == 1:
    key_list = [] #[0, 1, 2, 3, 4, 5]
    for i in range(0,ssdnet_Daten_zeile):
        key_list.append(i)
# Schritt2: Die Informationen konsolidieren, um eine Liste zu erstellen, die nur die Anzahl der Spalten enthält.
    zeile_list_element_1 = [[] for i in range(0,ssdnet_Daten_zeile)] #[[], [], [], [], [], []]
    zeile_list_element_2 = [[] for i in range(0,ssdnet_Daten_zeile)] #[[], [], [], [], [], []]
    for i in range(0,ssdnet_Daten_zeile):
        for j in range(0,len(ssdnet_list_index_such_element_1_matrix)):
            if ssdnet_list_index_such_element_1_matrix[0] == i:
                zeile_list_element_1[i].append(ssdnet_list_index_such_element_1_matrix[1])
    # zeile_list_element_1 =[[0, 2], [], [1], [], [1], []]
    for i in range(0,ssdnet_Daten_zeile):
        for j in range(0,len(ssdnet_list_index_such_element_2_matrix)):
            if ssdnet_list_index_such_element_2_matrix[0] == i:
                zeile_list_element_2[i].append(ssdnet_list_index_such_element_2_matrix[1])
    # zeile_list_element_2 =[[], [6], [6], [6], [], [4]]

# Schritt1: Erstellen einer Liste von Zeilenzählungen (ssdnet_Daten_zeile != 1)
if ssdnet_Daten_zeile != 1:
    key_list = []  # [0, 1, 2, 3, 4, 5]
    for i in range(0, ssdnet_Daten_zeile):
        key_list.append(i)
    # Schritt2: Die Informationen konsolidieren, um eine Liste zu erstellen, die nur die Anzahl der Spalten enthält.
    if type(ssdnet_list_index_such_element_1_matrix[0]) != int and type(ssdnet_list_index_such_element_2_matrix[0]) != int:
        zeile_list_element_1 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        zeile_list_element_2 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_1_matrix)):
                if ssdnet_list_index_such_element_1_matrix[j][0] == i:
                    zeile_list_element_1[i].append(ssdnet_list_index_such_element_1_matrix[j][1])
        # zeile_list_element_1 =[[0, 2], [], [1], [], [1], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_2_matrix)):
                if ssdnet_list_index_such_element_2_matrix[j][0] == i:
                    zeile_list_element_2[i].append(ssdnet_list_index_such_element_2_matrix[j][1])
        #zeile_list_element_2 =[[], [6], [6], [6], [], [4]]
    if type(ssdnet_list_index_such_element_1_matrix[0]) == int and type(ssdnet_list_index_such_element_2_matrix[0]) != int:
        zeile_list_element_1 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        zeile_list_element_2 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_1_matrix)):
                if ssdnet_list_index_such_element_1_matrix[0] == i:
                    zeile_list_element_1[i].append(ssdnet_list_index_such_element_1_matrix[1])
        # zeile_list_element_1 =[[0, 2], [], [1], [], [1], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_2_matrix)):
                if ssdnet_list_index_such_element_2_matrix[j][0] == i:
                    zeile_list_element_2[i].append(ssdnet_list_index_such_element_2_matrix[j][1])
        #zeile_list_element_2 =[[], [6], [6], [6], [], [4]]
    if type(ssdnet_list_index_such_element_1_matrix[0]) != int and type(ssdnet_list_index_such_element_2_matrix[0]) == int:
        zeile_list_element_1 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        zeile_list_element_2 = [[] for i in range(0, ssdnet_Daten_zeile)]  # [[], [], [], [], [], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_1_matrix)):
                if ssdnet_list_index_such_element_1_matrix[j][0] == i:
                    zeile_list_element_1[i].append(ssdnet_list_index_such_element_1_matrix[j][1])
        # zeile_list_element_1 =[[0, 2], [], [1], [], [1], []]
        for i in range(0, ssdnet_Daten_zeile):
            for j in range(0, len(ssdnet_list_index_such_element_2_matrix)):
                if ssdnet_list_index_such_element_2_matrix[0] == i:
                    zeile_list_element_2[i].append(ssdnet_list_index_such_element_2_matrix[1])
        # zeile_list_element_2 =[[], [6], [6], [6], [], [4]]
# Schritt3: Es werden zwei Wörterbücher erstellt, eines zum Abrufen von 0 und das andere zum Abrufen der Seitenlänge des Modells. Inhaltsverzeichnis ist die Anzahl der Zeilen in der Liste
dict_such_element_1 = dict(zip(key_list,zeile_list_element_1))
# dict_such_element_1 ={0: [0, 2], 1: [], 2: [1], 3: [], 4: [1], 5: []}
dict_such_element_2 = dict(zip(key_list,zeile_list_element_2))
# dict_such_element_2 ={0: [], 1: [6], 2: [6], 3: [6], 4: [], 5: [4]}

'''Das Ergebnis der Paarung der Bodenflächeninformationen des Merkmals auf dem Modell ablesen.'''
result_Daten = pd.read_csv(result_filepath)
result_Daten_zeile =result_Daten.shape[0]
result_list =result_Daten.values.tolist()

'''Eine Funktion zur Zerlegung der Ausgabe von SsdNet, wobei verschiedene Merkmale in getrennten Listen abgelegt werden.'''
def find(list):
    o_ring = []
    through_hole = []
    blind_hole =[]
    triangular_passage = []
    rectangular_passage = []
    circular_through_slot = []
    triangular_through_slot = []
    rectangular_through_slot = []
    rectangular_blind_slot = []
    triangular_pocket = []
    rectangular_pocket = []
    circular_end_pocket = []
    triangular_blind_step = []
    circular_blind_step = []
    rectangular_blind_step = []
    rectangular_through_step = []
    two_sides_through_step = []
    slanted_through_step = []
    chamfer = []
    round = []
    vertical_circular_end_blind_slot = []
    horizontal_circular_end_blind_slot = []
    six_sides_passage = []
    six_sides_pocket = []
    for i, x in enumerate(list):
        if x == 0.0:
            o_ring.append(i)
        elif x == 1.0:
            through_hole.append(i)
        elif x == 2.0:
            blind_hole.append(i)
        elif x == 3.0:
            triangular_passage.append(i)
        elif x == 4.0:
            rectangular_passage.append(i)
        elif x == 5.0:
            circular_through_slot.append(i)
        elif x == 6.0:
            triangular_through_slot.append(i)
        elif x == 7.0:
            rectangular_through_slot.append(i)
        elif x == 8.0:
            rectangular_blind_slot.append(i)
        elif x == 9.0:
            triangular_pocket.append(i)
        elif x == 10.0:
            rectangular_pocket.append(i)
        elif x == 11.0:
            circular_end_pocket.append(i)
        elif x == 12.0:
            triangular_blind_step.append(i)
        elif x == 13.0:
            circular_blind_step.append(i)
        elif x == 14.0:
            rectangular_blind_step.append(i)
        elif x == 15.0:
            rectangular_through_step.append(i)
        elif x == 16.0:
            two_sides_through_step.append(i)
        elif x == 17.0:
            slanted_through_step.append(i)
        elif x == 18.0:
            chamfer.append(i)
        elif x == 19.0:
            round.append(i)
        elif x == 20.0:
            vertical_circular_end_blind_slot.append(i)
        elif x == 21.0:
            horizontal_circular_end_blind_slot.append(i)
        elif x == 22.0:
            six_sides_passage.append(i)
        elif x == 23.0:
            six_sides_pocket.append(i)
    return  o_ring,through_hole,blind_hole,triangular_passage,rectangular_passage,\
            circular_through_slot,triangular_through_slot,rectangular_through_slot,rectangular_blind_slot,\
            triangular_pocket,rectangular_pocket,circular_end_pocket,triangular_blind_step,\
            circular_blind_step,rectangular_blind_step,rectangular_through_step,two_sides_through_step,\
            slanted_through_step,chamfer,round,vertical_circular_end_blind_slot,horizontal_circular_end_blind_slot,\
            six_sides_passage,six_sides_pocket

'''Ein Wörterbuch mit Merkmalsnummern als Abfrage erstellen, und der Inhalt ist die Anzahl der Zeilen, die den Merkmalen entsprechen.'''
no_same_list = list(set(result_Daten['Type'].values.tolist()))# delete same parameter set会自动排序，主要是自己写的那个find函数也是按顺寻排序的
Type_result = result_Daten['Type'].values.tolist() #dataframe的type整合为列表[2.0, 2.0, 14.0, 10.0, 10.0, 2.0]
no_zero_list = [i for i in list(find(Type_result)) if i !=[]]
dict_all = dict(zip(no_same_list,no_zero_list))# 整合字典，SSDNET给出的列表是没有顺序的
# Beispiel: dict_all ={2.0: [0, 1, 5], 10.0: [3, 4], 14.0: [2]}, Merkmal 14 steht in Zeile 2 der Liste.

'''Wenn das bearbeitbare Merkmal im Wörterbuch enthalten ist, wird eine entsprechende Liste ausgegeben, 
die die der Anzahl der Merkmalszeilen entsprechende Merkmalsbasis-ID enthält.'''
if 2.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0,len(dict_all[2.0]))] #[[],[]]
    rectangular_pocket_face_id = [[] for i in range(0,len(dict_all[2.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[2.0])):
        face_id = dict_all[2.0][i] #[3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    # rectangular_pocket_face_id =[[30, 8, 22, 21, 24, 23], [16, 18, 5, 15, 28, 17]]
    # zeile_element_1 =[[], [1]]
    # zeile_element_2 =[[6], []]
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[2.0])): #[3,4]
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    #print("bottom_face_zeile_list",bottom_face_zeile_list) #[[6], [1]]
    blind_hole_bottom_face_line = [[] for i in range(0,len(dict_all[2.0]))]
    for i in range(0, len(dict_all[2.0])): # Wenn das Element in der Liste den Erwartungen entspricht, wird die entsprechende Basis-ID in die Liste geschrieben.
        for j in range(0,len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[2.0][i]][6]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[2.0][i]][5]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[2.0][i]][3]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[2.0][i]][4]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[2.0][i]][7]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[2.0][i]][2]
                blind_hole_bottom_face_line[i].append(bottom_face_id)
    # blind_hole_bottom_face_line =[[30.0], [28.0]]
if 10.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0,len(dict_all[10.0]))] #[[],[]]
    rectangular_pocket_face_id = [[] for i in range(0,len(dict_all[10.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[10.0])):
        face_id = dict_all[10.0][i] #[3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j])) #切片选择boundbox所有面
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[10.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0,len(dict_all[10.0]))]
    for i in range(0, len(dict_all[10.0])):
        for j in range(0,len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[10.0][i]][6]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[10.0][i]][5]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[10.0][i]][3]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[10.0][i]][4]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[10.0][i]][7]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[10.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    rechtgular_face_line = bottom_face_line
if 14.0 in dict_all: # Die Blindstufe ist relativ speziell, denn die Blindstufe hat bis zu drei Gesichter in der äußersten Position des Modells.
    rectangular_pocket_face = [[] for i in range(0,len(dict_all[14.0]))] #[[],[]]
    rectangular_pocket_face_id = [[] for i in range(0,len(dict_all[14.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[14.0])):
        face_id = dict_all[14.0][i] #[3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[14.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0,len(dict_all[14.0]))]

    for i in range(0, len(dict_all[14.0])):
        for j in range(0,len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][2]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 1 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][5]<=modell_länge and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=modell_länge and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][5]<=modell_länge and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=modell_länge and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][6]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=5 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][2]<=5:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][2]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][4]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6 and 0<=ssdnet_Daten.iloc[dict_all[14.0][i]][1]<=5 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][5]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6 and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][4]<=modell_länge and modell_länge-5<=ssdnet_Daten.iloc[dict_all[14.0][i]][5]<=modell_länge:
                bottom_face_id = result_list[dict_all[14.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    blind_step_bottom_face_line = bottom_face_line
    blind_step_bottom_face_line_no_same = []
    for i in range (0, len(dict_all[14.0])):
        blind_step_bottom_face_line_no_same.append(list(set(blind_step_bottom_face_line[i])))
    #print("blind_step_bottom_face_line:",blind_step_bottom_face_line_no_same) #[[ 6.0]]
if 7.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[7.0]))]  # [[],[]]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[7.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[7.0])):
        face_id = dict_all[7.0][i]  # [3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[7.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[7.0]))]
    for i in range(0, len(dict_all[7.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[7.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    rechtgular_through_slot_face_line = bottom_face_line
if 8.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[8.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[8.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[8.0])):
        face_id = dict_all[8.0][i]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[8.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[8.0]))]
    for i in range(0, len(dict_all[8.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    rechtgular_blind_slot_face_line = bottom_face_line
if 9.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[9.0]))]  # [[],[]]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[9.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[9.0])):
        face_id = dict_all[9.0][i]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[9.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[9.0]))]
    for i in range(0, len(dict_all[9.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[9.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    triangular_pocket_face_line = bottom_face_line
if 12.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[8.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[8.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[8.0])):
        face_id = dict_all[8.0][i]  # [3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[8.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[8.0]))]
    for i in range(0, len(dict_all[8.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[8.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    triangular_blind_step_face_line = bottom_face_line
if 13.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[13.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[13.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[13.0])):
        face_id = dict_all[13.0][i]  # [3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[13.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[13.0]))]
    for i in range(0, len(dict_all[13.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[13.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    circular_blind_step_face_line = bottom_face_line
if 15.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[15.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[15.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[15.0])):
        face_id = dict_all[10.0][i]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[15.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[15.0]))]
    for i in range(0, len(dict_all[15.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[15.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    rechtangular_through_step_face_line = bottom_face_line
if 17.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[17.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[17.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[17.0])):
        face_id = dict_all[17.0][i]  # [3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[17.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[17.0]))]
    for i in range(0, len(dict_all[17.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[17.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    slanted_through_step_face_line = bottom_face_line
if 20.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[20.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[20.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[20.0])):
        face_id = dict_all[20.0][i]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[20.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[10.0]))]
    for i in range(0, len(dict_all[20.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[20.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    vertical_circular_end_blind_slot_face_line = bottom_face_line
if 21.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[21.0]))]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[21.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[21.0])):
        face_id = dict_all[21.0][i]  # [3,4]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[21.0])):
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    bottom_face_line = [[] for i in range(0, len(dict_all[21.0]))]
    for i in range(0, len(dict_all[21.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[21.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    horizontal_circular_end_blind_slot_face_line = bottom_face_line
if 23.0 in dict_all:
    rectangular_pocket_face = [[] for i in range(0, len(dict_all[23.0]))]  # [[],[]]
    rectangular_pocket_face_id = [[] for i in range(0, len(dict_all[23.0]))]
    zeile_element_1 = []
    zeile_element_2 = []
    for i in range(0, len(dict_all[23.0])):
        face_id = dict_all[23.0][i]
        zeile_element_1.append(dict_such_element_1[face_id])
        zeile_element_2.append(dict_such_element_2[face_id])
        for j in range(2, 8):
            facName = 'Face{:d}'.format(int(result_Daten.iloc[face_id][j]))  # 切片选择boundbox所有面
            id = int(result_Daten.iloc[face_id][j])
            rectangular_pocket_face[i].append(facName)
            rectangular_pocket_face_id[i].append(id)
    bottom_face_zeile_list = []
    for i in range(0, len(dict_all[23.0])):  # [3,4]
        append_list = zeile_element_1[i] + zeile_element_2[i]
        bottom_face_zeile_list.append(append_list)
    # print("bottom_face_zeile_list",bottom_face_zeile_list) #[[6], [1]]
    bottom_face_line = [[] for i in range(0, len(dict_all[23.0]))]
    for i in range(0, len(dict_all[23.0])):
        for j in range(0, len(bottom_face_zeile_list[i])):
            if bottom_face_zeile_list[i][j] == 1:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 2:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 3:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 4:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 5:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
            if bottom_face_zeile_list[i][j] == 6:
                bottom_face_id = result_list[dict_all[23.0][i]][2]
                bottom_face_line[i].append(bottom_face_id)
    six_sides_pocket_face_line = bottom_face_line

'''Öffnen Sie das Modell nach der booleschen Operation "Common.FCStd"'''
DOC = App.openDocument(filepath)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()

'''Erstellen von Schwerpunkten für jede ausgewählte Fläche'''
# rechtaugular pocket
if 10.0 in dict_all:
    pocket_centermass_list = []
    for i in range(0,len(rechtgular_face_line)):
        pocket_center_face =  App.ActiveDocument.Common.Shape.Faces[int(rechtgular_face_line[i][0]-1)]
        pocket_centermass = pocket_center_face.CenterOfMass
        pocket_centermass_list.append(list(pocket_centermass))
# print("pocket_centermass",pocket_centermass_list) #[[21.0, 20.0, 30.0], [10.0, 20.0, 20.0]]
# blind hole
if 2.0 in dict_all:
    blind_hole_centermass_list = []
    for i in range(0,len(blind_hole_bottom_face_line)):
        blind_hole_center_face = App.ActiveDocument.Common.Shape.Faces[int(blind_hole_bottom_face_line[i][0]-1)]
        blind_hole_centermass = blind_hole_center_face.CenterOfMass
        blind_hole_centermass_list.append(list(blind_hole_centermass))
# blind step
if 14.0 in dict_all:
    blind_step_centermass_list = []
    for i in range(0,len(blind_step_bottom_face_line_no_same)):
        blind_step_center_face = App.ActiveDocument.Common.Shape.Faces[int(blind_step_bottom_face_line_no_same[i][0]-1)]
        blind_step_centermass = blind_step_center_face.CenterOfMass
        blind_step_centermass_list.append(list(blind_step_centermass))
# rechtgular_through_slot
if 7.0 in dict_all:
    rechtgular_through_slot_centermass_list = []
    for i in range(0,len(rechtgular_face_line)):
        rechtgular_through_slot_center_face =  App.ActiveDocument.Common.Shape.Faces[int(rechtgular_through_slot_face_line[i][0]-1)]
        rechtgular_through_slot_centermass = rechtgular_through_slot_center_face.CenterOfMass
        rechtgular_through_slot_centermass_list.append(list(rechtgular_through_slot_centermass))
# rechtgular_blind_slot
if 8.0 in dict_all:
    rechtgular_blind_slot_centermass_list = []
    for i in range(0,len(rechtgular_blind_slot_face_line)):
        rechtgular_blind_slot_center_face =  App.ActiveDocument.Common.Shape.Faces[int(rechtgular_blind_slot_face_line[i][0]-1)]
        rechtgular_blind_slot_centermass = rechtgular_blind_slot_center_face.CenterOfMass
        rechtgular_blind_slot_centermass_list.append(list(rechtgular_blind_slot_centermass))
# triangular_pocket
if 9.0 in dict_all:
    triangular_pocket_centermass_list = []
    for i in range(0,len(triangular_pocket_face_line)):
        triangular_pocket_center_face =  App.ActiveDocument.Common.Shape.Faces[int(triangular_pocket_face_line[i][0]-1)]
        triangular_pocket_centermass = triangular_pocket_center_face.CenterOfMass
        triangular_pocket_centermass_list.append(list(triangular_pocket_centermass))
# triangular_blind_step
if 12.0 in dict_all:
    triangular_blind_step_centermass_list = []
    for i in range(0,len(rechtgular_blind_slot_face_line)):
        triangular_blind_step_center_face =  App.ActiveDocument.Common.Shape.Faces[int(triangular_blind_step_face_line[i][0]-1)]
        triangular_blind_step_centermass = triangular_blind_step_center_face.CenterOfMass
        triangular_blind_step_centermass_list.append(list(triangular_blind_step_centermass))
# circular_blind_step
if 13.0 in dict_all:
    circular_blind_step_centermass_list = []
    for i in range(0, len(circular_blind_step_face_line)):
        circular_blind_step_center_face = App.ActiveDocument.Common.Shape.Faces[int(circular_blind_step_face_line[i][0] - 1)]
        circular_blind_step_centermass = circular_blind_step_center_face.CenterOfMass
        circular_blind_step_centermass_list.append(list(circular_blind_step_centermass))
# rechtangular_through_step
if 15.0 in dict_all:
    rechtangular_through_step_centermass_list = []
    for i in range(0, len(circular_blind_step_face_line)):
        rechtangular_through_step_center_face = App.ActiveDocument.Common.Shape.Faces[int(rechtangular_through_step_face_line[i][0] - 1)]
        rechtangular_through_step_centermass = rechtangular_through_step_center_face.CenterOfMass
        rechtangular_through_step_centermass_list.append(list(rechtangular_through_step_centermass))
# slanted_through_step
if 17.0 in dict_all:
    slanted_through_step_centermass_list = []
    for i in range(0, len(circular_blind_step_face_line)):
        slanted_through_step_center_face = App.ActiveDocument.Common.Shape.Faces[
            int(slanted_through_step_face_line[i][0] - 1)]
        slanted_through_step_centermass = slanted_through_step_center_face.CenterOfMass
        slanted_through_step_centermass_list.append(list(slanted_through_step_centermass))
# vertical_circular_end_blind_slot
if 20.0 in dict_all:
    vertical_circular_end_blind_slot_centermass_list = []
    for i in range(0, len(vertical_circular_end_blind_slot_face_line)):
        vertical_circular_end_blind_slot_center_face = App.ActiveDocument.Common.Shape.Faces[
            int(vertical_circular_end_blind_slot_face_line[i][0] - 1)]
        vertical_circular_end_blind_slot_centermass = vertical_circular_end_blind_slot_center_face.CenterOfMass
        vertical_circular_end_blind_slot_centermass_list.append(list(vertical_circular_end_blind_slot_centermass))
# horizontal_circular_end_blind_slot
if 21.0 in dict_all:
    horizontal_circular_end_blind_slot_centermass_list = []
    for i in range(0, len(horizontal_circular_end_blind_slot_face_line)):
        horizontal_circular_end_blind_slot_center_face = App.ActiveDocument.Common.Shape.Faces[
            int(horizontal_circular_end_blind_slot_face_line[i][0] - 1)]
        horizontal_circular_end_blind_slot_centermass = horizontal_circular_end_blind_slot_center_face.CenterOfMass
        horizontal_circular_end_blind_slot_centermass_list.append(list(horizontal_circular_end_blind_slot_centermass))
# six_sides_pocket
if 23.0 in dict_all:
    six_sides_pocket_centermass_list = []
    for i in range(0, len(six_sides_pocket_face_line)):
        six_sides_pocket_center_face = App.ActiveDocument.Common.Shape.Faces[
            int(six_sides_pocket_face_line[i][0] - 1)]
        six_sides_pocket_centermass = six_sides_pocket_center_face.CenterOfMass
        six_sides_pocket_centermass_list.append(list(six_sides_pocket_centermass))


'''Es ist notwendig, die Gesichter aller Operationen zu klassifizieren und ein Wörterbuch mit 5 Verarbeitungsgesichtern als Grundlage für jede Verarbeitung zu erstellen'''
# rechgular_pocket
if 10.0 in dict_all:
    pocket_normal = []
    for i in range(0,len(rechtgular_face_line)):
        pocket_face = App.ActiveDocument.Common.Shape.Faces[int(rechtgular_face_line[i][0]-1)]
        pocket_face_normal = pocket_face.normalAt(0,0)
        pocket_normal.append(list(pocket_face_normal))
    # mit Ausnahme aller -0,0
    pocket_normal_korr = []
    for i in range(0, len(pocket_normal)):
        rep = [0.0 if x == -0.0 else x for x in pocket_normal[i]]
        pocket_normal_korr.append(rep)
    # Bearbeitete Merkmale werden in einzelne Flächen unterteilt
    pocket_top = []
    pocket_site1= []
    pocket_site2= []
    pocket_site3= []
    pocket_site4= []
    for i in range(0, len(pocket_normal_korr)):
        if pocket_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = pocket_normal_korr[i] + [i]
            pocket_top.append(a)
        if pocket_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = pocket_normal_korr[i] + [i]
            pocket_site1.append(a)
        if pocket_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = pocket_normal_korr[i] + [i]
            pocket_site2.append(a)
        if pocket_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = pocket_normal_korr[i] + [i]
            pocket_site3.append(a)
        if pocket_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = pocket_normal_korr[i] + [i]
            pocket_site4.append(a)
    #print(pocket_top,pocket_site1,pocket_site2,pocket_site3,pocket_site4) #[[0.0, 0.0, 1.0, 0]] [[-1.0, 0.0, 0.0, 1]] [] [] []
# Step2 建立针对各个面加工的字典
    pocket_operation_face_list = ['Top','Site1','Site2','Site3','Site4']
    pocket_operation_normal_list = [pocket_top,pocket_site1,pocket_site2,pocket_site3,pocket_site4]
    pocket_operation_dict = dict(zip(pocket_operation_face_list,pocket_operation_normal_list))
    print("pocket_dict:",pocket_operation_dict) #{'Top': [[0.0, 0.0, 1.0, 0]], 'Site1': [[-1.0, 0.0, 0.0, 1]], 'Site2': [], 'Site3': [], 'Site4': []}
# blind_hole
if 2.0 in dict_all:
    blind_hole_normal = []
    for i in range(0,len(blind_hole_bottom_face_line)):
        blind_hole_face = App.ActiveDocument.Common.Shape.Faces[int(blind_hole_bottom_face_line[i][0]-1)]
        blind_hole_face_normal = blind_hole_face.normalAt(0,0)
        blind_hole_normal.append(list(blind_hole_face_normal))

    blind_hole_normal_korr = []
    for i in range(0, len(blind_hole_normal)):
        rep = [0.0 if x == -0.0 else x for x in blind_hole_normal[i]]
        blind_hole_normal_korr.append(rep)

    blind_hole_top = []
    blind_hole_site1= []
    blind_hole_site2= []
    blind_hole_site3= []
    blind_hole_site4= []
    for i in range(0, len(blind_hole_normal_korr)):
        if blind_hole_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = blind_hole_normal_korr[i] + [i]
            blind_hole_top.append(a)
        if blind_hole_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = blind_hole_normal_korr[i] + [i]
            blind_hole_site1.append(a)
        if blind_hole_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = blind_hole_normal_korr[i] + [i]
            blind_hole_site2.append(a)
        if blind_hole_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = blind_hole_normal_korr[i] + [i]
            blind_hole_site3.append(a)
        if blind_hole_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = blind_hole_normal_korr[i] + [i]
            blind_hole_site4.append(a)

    blind_hole_operation_face_list = ['Top','Site1','Site2','Site3','Site4']
    blind_hole_operation_normal_list = [blind_hole_top,blind_hole_site1,blind_hole_site2,blind_hole_site3,blind_hole_site4]
    blind_hole_operation_dict = dict(zip(blind_hole_operation_face_list,blind_hole_operation_normal_list))
    #print("blind_hole dict:",blind_hole_operation_dict) #{'Top': [[0.0, 0.0, 1.0, 1]], 'Site1': [], 'Site2': [], 'Site3': [[1.0, 0.0, 0.0, 2]], 'Site4': [[0.0, -1.0, 0.0, 0]]}
# blind_step
if 14.0 in dict_all:
    blind_step_normal = []
    for i in range(0,len(blind_step_bottom_face_line_no_same)):
        blind_step_face = App.ActiveDocument.Common.Shape.Faces[int(blind_step_bottom_face_line_no_same[i][0]-1)]
        blind_step_face_normal = blind_step_face.normalAt(0,0)
        blind_step_normal.append(list(blind_step_face_normal))

    blind_step_normal_korr = []
    for i in range(0, len(blind_step_normal)):
        rep = [0.0 if x == -0.0 else x for x in blind_step_normal[i]]
        blind_step_normal_korr.append(rep)

    blind_step_top = []
    blind_step_site1= []
    blind_step_site2= []
    blind_step_site3= []
    blind_step_site4= []
    for i in range(0, len(blind_step_normal_korr)):
        if blind_step_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = blind_step_normal_korr[i] + [i]
            blind_step_top.append(a)
        if blind_step_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = blind_step_normal_korr[i] + [i]
            blind_step_site1.append(a)
        if blind_step_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = blind_step_normal_korr[i] + [i]
            blind_step_site2.append(a)
        if blind_step_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = blind_step_normal_korr[i] + [i]
            blind_step_site3.append(a)
        if blind_step_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = blind_step_normal_korr[i] + [i]
            blind_step_site4.append(a)

    blind_step_operation_face_list = ['Top','Site1','Site2','Site3','Site4']
    blind_step_operation_normal_list = [blind_step_top,blind_step_site1,blind_step_site2,blind_step_site3,blind_step_site4]
    blind_step_operation_dict = dict(zip(blind_step_operation_face_list,blind_step_operation_normal_list))
    #print("blind_step_dict:",blind_step_operation_dict) #{'Top': [[0.0, 0.0, 1.0, 0]], 'Site1': [], 'Site2': [], 'Site3': [], 'Site4': []}
# rechtgular_through_slot
if 7.0 in dict_all:
    rechtgular_through_slot_normal = []
    for i in range(0, len(rechtgular_through_slot_face_line)):
        rechtgular_through_slot_face = App.ActiveDocument.Common.Shape.Faces[int(rechtgular_through_slot_face_line[i][0] - 1)]
        rechtgular_through_slot_face_normal = rechtgular_through_slot_face.normalAt(0, 0)
        rechtgular_through_slot_normal.append(list(rechtgular_through_slot_face_normal))

    rechtgular_through_slot_normal_korr = []
    for i in range(0, len(rechtgular_through_slot_normal)):
        rep = [0.0 if x == -0.0 else x for x in rechtgular_through_slot_normal[i]]
        rechtgular_through_slot_normal_korr.append(rep)

    rechtgular_through_slot_top = []
    rechtgular_through_slot_site1 = []
    rechtgular_through_slot_site2 = []
    rechtgular_through_slot_site3 = []
    rechtgular_through_slot_site4 = []
    for i in range(0, len(rechtgular_through_slot_normal_korr)):
        if rechtgular_through_slot_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = rechtgular_through_slot_normal_korr[i] + [i]
            rechtgular_through_slot_top.append(a)
        if rechtgular_through_slot_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = rechtgular_through_slot_normal_korr[i] + [i]
            rechtgular_through_slot_site1.append(a)
        if rechtgular_through_slot_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = rechtgular_through_slot_normal_korr[i] + [i]
            rechtgular_through_slot_site2.append(a)
        if rechtgular_through_slot_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = rechtgular_through_slot_normal_korr[i] + [i]
            rechtgular_through_slot_site3.append(a)
        if rechtgular_through_slot_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = rechtgular_through_slot_normal_korr[i] + [i]
            rechtgular_through_slot_site4.append(a)

    rechtgular_through_slot_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    rechtgular_through_slot_operation_normal_list = [rechtgular_through_slot_top, rechtgular_through_slot_site1, rechtgular_through_slot_site2, rechtgular_through_slot_site3, rechtgular_through_slot_site4]
    rechtgular_through_slot_operation_dict = dict(zip(rechtgular_through_slot_operation_face_list, rechtgular_through_slot_operation_normal_list))
# rechtgular_blind_slot
if 8.0 in dict_all:
    rechtgular_blind_slot_normal = []
    for i in range(0, len(rechtgular_blind_slot_face_line)):
        rechtgular_blind_slot_face = App.ActiveDocument.Common.Shape.Faces[int(rechtgular_blind_slot_face_line[i][0] - 1)]
        rechtgular_blind_slot_face_normal = rechtgular_blind_slot_face.normalAt(0, 0)
        rechtgular_blind_slot_normal.append(list(rechtgular_blind_slot_face_normal))

    rechtgular_blind_slot_normal_korr = []
    for i in range(0, len(rechtgular_blind_slot_normal)):
        rep = [0.0 if x == -0.0 else x for x in rechtgular_blind_slot_normal[i]]
        rechtgular_blind_slot_normal_korr.append(rep)

    rechtgular_blind_slot_top = []
    rechtgular_blind_slot_site1 = []
    rechtgular_blind_slot_site2 = []
    rechtgular_blind_slot_site3 = []
    rechtgular_blind_slot_site4 = []
    for i in range(0, len(rechtgular_blind_slot_normal_korr)):
        if rechtgular_blind_slot_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = rechtgular_blind_slot_normal_korr[i] + [i]
            rechtgular_blind_slot_top.append(a)
        if rechtgular_blind_slot_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = rechtgular_blind_slot_normal_korr[i] + [i]
            rechtgular_blind_slot_site1.append(a)
        if rechtgular_blind_slot_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = rechtgular_blind_slot_normal_korr[i] + [i]
            rechtgular_blind_slot_site2.append(a)
        if rechtgular_blind_slot_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = rechtgular_blind_slot_normal_korr[i] + [i]
            rechtgular_blind_slot_site3.append(a)
        if rechtgular_blind_slot_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = rechtgular_blind_slot_normal_korr[i] + [i]
            rechtgular_blind_slot_site4.append(a)

    rechtgular_blind_slot_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    rechtgular_blind_slot_operation_normal_list = [rechtgular_blind_slot_top, rechtgular_blind_slot_site1,
                                                   rechtgular_blind_slot_site2, rechtgular_blind_slot_site3, rechtgular_blind_slot_site4]
    rechtgular_blind_slot_operation_dict = dict(zip(rechtgular_blind_slot_operation_face_list, rechtgular_blind_slot_operation_normal_list))
# triangular_pocket
if 9.0 in dict_all:
    triangular_pocket_normal = []
    for i in range(0, len(triangular_pocket_face_line)):
        triangular_pocket_face = App.ActiveDocument.Common.Shape.Faces[int(triangular_pocket_face_line[i][0] - 1)]
        triangular_pocket_face_normal = triangular_pocket_face.normalAt(0, 0)
        triangular_pocket_normal.append(list(triangular_pocket_face_normal))

    triangular_pocket_normal_korr = []
    for i in range(0, len(triangular_pocket_normal)):
        rep = [0.0 if x == -0.0 else x for x in triangular_pocket_normal[i]]
        triangular_pocket_normal_korr.append(rep)

    triangular_pocket_top = []
    triangular_pocket_site1 = []
    triangular_pocket_site2 = []
    triangular_pocket_site3 = []
    triangular_pocket_site4 = []
    for i in range(0, len(triangular_pocket_normal_korr)):
        if triangular_pocket_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = triangular_pocket_normal_korr[i] + [i]
            triangular_pocket_top.append(a)
        if triangular_pocket_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = triangular_pocket_normal_korr[i] + [i]
            triangular_pocket_site1.append(a)
        if triangular_pocket_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = triangular_pocket_normal_korr[i] + [i]
            triangular_pocket_site2.append(a)
        if triangular_pocket_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = triangular_pocket_normal_korr[i] + [i]
            triangular_pocket_site3.append(a)
        if triangular_pocket_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = triangular_pocket_normal_korr[i] + [i]
            triangular_pocket_site4.append(a)

    triangular_pocket_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    triangular_pocket_operation_normal_list = [triangular_pocket_top, triangular_pocket_site1,
                                                   triangular_pocket_site2, triangular_pocket_site3, triangular_pocket_site4]
    triangular_pocket_operation_dict = dict(zip(triangular_pocket_operation_face_list, triangular_pocket_operation_normal_list))
# triangular_blind_step
if 12.0 in dict_all:
    triangular_blind_step_normal = []
    for i in range(0, len(rechtgular_blind_slot_face_line)):
        triangular_blind_step_face = App.ActiveDocument.Common.Shape.Faces[int(triangular_blind_step_face_line[i][0] - 1)]
        triangular_blind_step_face_normal = triangular_blind_step_face.normalAt(0, 0)
        triangular_blind_step_normal.append(list(triangular_blind_step_face_normal))

    triangular_blind_step_normal_korr = []
    for i in range(0, len(triangular_blind_step_normal)):
        rep = [0.0 if x == -0.0 else x for x in triangular_blind_step_normal[i]]
        triangular_blind_step_normal_korr.append(rep)

    triangular_blind_step_top = []
    triangular_blind_step_site1 = []
    triangular_blind_step_site2 = []
    triangular_blind_step_site3 = []
    triangular_blind_step_site4 = []
    for i in range(0, len(triangular_blind_step_normal_korr)):
        if triangular_blind_step_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = triangular_blind_step_normal_korr[i] + [i]
            triangular_blind_step_top.append(a)
        if triangular_blind_step_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = triangular_blind_step_normal_korr[i] + [i]
            triangular_blind_step_site1.append(a)
        if triangular_blind_step_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = triangular_blind_step_normal_korr[i] + [i]
            triangular_blind_step_site2.append(a)
        if triangular_blind_step_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = triangular_blind_step_normal_korr[i] + [i]
            triangular_blind_step_site3.append(a)
        if triangular_blind_step_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = triangular_blind_step_normal_korr[i] + [i]
            triangular_blind_step_site4.append(a)

    triangular_blind_step_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    triangular_blind_step_operation_normal_list = [triangular_blind_step_top, triangular_blind_step_site1,
                                                   triangular_blind_step_site2, triangular_blind_step_site3, triangular_blind_step_site4]
    triangular_blind_step_operation_dict = dict(zip(triangular_blind_step_operation_face_list, triangular_blind_step_operation_normal_list))
# circular_blind_step
if 13.0 in dict_all:
    circular_blind_step_normal = []
    for i in range(0, len(circular_blind_step_face_line)):
        circular_blind_step_face = App.ActiveDocument.Common.Shape.Faces[
            int(circular_blind_step_face_line[i][0] - 1)]
        circular_blind_step_face_normal = circular_blind_step_face.normalAt(0, 0)
        circular_blind_step_normal.append(list(circular_blind_step_face_normal))

    circular_blind_step_normal_korr = []
    for i in range(0, len(circular_blind_step_normal)):
        rep = [0.0 if x == -0.0 else x for x in circular_blind_step_normal[i]]
        circular_blind_step_normal_korr.append(rep)

    circular_blind_step_top = []
    circular_blind_step_site1 = []
    circular_blind_step_site2 = []
    circular_blind_step_site3 = []
    circular_blind_step_site4 = []
    for i in range(0, len(circular_blind_step_normal_korr)):
        if circular_blind_step_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = circular_blind_step_normal_korr[i] + [i]
            circular_blind_step_top.append(a)
        if circular_blind_step_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = circular_blind_step_normal_korr[i] + [i]
            circular_blind_step_site1.append(a)
        if circular_blind_step_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = circular_blind_step_normal_korr[i] + [i]
            circular_blind_step_site2.append(a)
        if circular_blind_step_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = circular_blind_step_normal_korr[i] + [i]
            circular_blind_step_site3.append(a)
        if circular_blind_step_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = circular_blind_step_normal_korr[i] + [i]
            circular_blind_step_site4.append(a)

    circular_blind_step_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    circular_blind_step_operation_normal_list = [circular_blind_step_top, circular_blind_step_site1,
                                                   circular_blind_step_site2, circular_blind_step_site3,
                                                   circular_blind_step_site4]
    circular_blind_step_operation_dict = dict(
        zip(circular_blind_step_operation_face_list, circular_blind_step_operation_normal_list))
# rechtangular_through_step
if 15.0 in dict_all:
    rechtangular_through_step_normal = []
    for i in range(0, len(rechtangular_through_step_face_line)):
        rechtangular_through_step_face = App.ActiveDocument.Common.Shape.Faces[
            int(rechtangular_through_step_face_line[i][0] - 1)]
        rechtangular_through_step_face_normal = rechtangular_through_step_face.normalAt(0, 0)
        rechtangular_through_step_normal.append(list(rechtangular_through_step_face_normal))

    rechtangular_through_step_normal_korr = []
    for i in range(0, len(rechtangular_through_step_normal)):
        rep = [0.0 if x == -0.0 else x for x in rechtangular_through_step_normal[i]]
        rechtangular_through_step_normal_korr.append(rep)

    rechtangular_through_step_top = []
    rechtangular_through_step_site1 = []
    rechtangular_through_step_site2 = []
    rechtangular_through_step_site3 = []
    rechtangular_through_step_site4 = []
    for i in range(0, len(rechtangular_through_step_normal_korr)):
        if rechtangular_through_step_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = rechtangular_through_step_normal_korr[i] + [i]
            rechtangular_through_step_top.append(a)
        if rechtangular_through_step_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = rechtangular_through_step_normal_korr[i] + [i]
            rechtangular_through_step_site1.append(a)
        if rechtangular_through_step_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = rechtangular_through_step_normal_korr[i] + [i]
            rechtangular_through_step_site2.append(a)
        if rechtangular_through_step_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = rechtangular_through_step_normal_korr[i] + [i]
            rechtangular_through_step_site3.append(a)
        if rechtangular_through_step_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = rechtangular_through_step_normal_korr[i] + [i]
            rechtangular_through_step_site4.append(a)

    rechtangular_through_step_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    rechtangular_through_step_operation_normal_list = [rechtangular_through_step_top, rechtangular_through_step_site1,
                                                 rechtangular_through_step_site2, rechtangular_through_step_site3,
                                                 rechtangular_through_step_site4]
    rechtangular_through_step_operation_dict = dict(
        zip(rechtangular_through_step_operation_face_list, rechtangular_through_step_operation_normal_list))
# slanted_through_step
if 17.0 in dict_all:
    slanted_through_step_normal = []
    for i in range(0, len(slanted_through_step_face_line)):
        slanted_through_step_face = App.ActiveDocument.Common.Shape.Faces[
            int(slanted_through_step_face_line[i][0] - 1)]
        slanted_through_step_face_normal = slanted_through_step_face.normalAt(0, 0)
        slanted_through_step_normal.append(list(slanted_through_step_face_normal))
    # 排除所有-0.0
    slanted_through_step_normal_korr = []
    for i in range(0, len(slanted_through_step_normal)):
        rep = [0.0 if x == -0.0 else x for x in slanted_through_step_normal[i]]
        slanted_through_step_normal_korr.append(rep)
    # 加工特征分到各个表面
    slanted_through_step_top = []
    slanted_through_step_site1 = []
    slanted_through_step_site2 = []
    slanted_through_step_site3 = []
    slanted_through_step_site4 = []
    for i in range(0, len(slanted_through_step_normal_korr)):
        if slanted_through_step_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = slanted_through_step_normal_korr[i] + [i]
            slanted_through_step_top.append(a)
        if slanted_through_step_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = slanted_through_step_normal_korr[i] + [i]
            slanted_through_step_site1.append(a)
        if slanted_through_step_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = slanted_through_step_normal_korr[i] + [i]
            slanted_through_step_site2.append(a)
        if slanted_through_step_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = slanted_through_step_normal_korr[i] + [i]
            slanted_through_step_site3.append(a)
        if slanted_through_step_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = slanted_through_step_normal_korr[i] + [i]
            slanted_through_step_site4.append(a)
    # Step2 建立针对各个面加工的字典
    slanted_through_step_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    slanted_through_step_operation_normal_list = [slanted_through_step_top, slanted_through_step_site1,
                                                 slanted_through_step_site2, slanted_through_step_site3,
                                                 slanted_through_step_site4]
    slanted_through_step_operation_dict = dict(
        zip(slanted_through_step_operation_face_list, slanted_through_step_operation_normal_list))
# vertical_circular_end_blind_slot
if 20.0 in dict_all:
    vertical_circular_end_blind_slot_normal = []
    for i in range(0, len(vertical_circular_end_blind_slot_face_line)):
        vertical_circular_end_blind_slot_face = App.ActiveDocument.Common.Shape.Faces[
            int(vertical_circular_end_blind_slot_face_line[i][0] - 1)]
        vertical_circular_end_blind_slot_face_normal = vertical_circular_end_blind_slot_face.normalAt(0, 0)
        vertical_circular_end_blind_slot_normal.append(list(vertical_circular_end_blind_slot_face_normal))

    vertical_circular_end_blind_slot_normal_korr = []
    for i in range(0, len(vertical_circular_end_blind_slot_normal)):
        rep = [0.0 if x == -0.0 else x for x in vertical_circular_end_blind_slot_normal[i]]
        vertical_circular_end_blind_slot_normal_korr.append(rep)

    vertical_circular_end_blind_slot_top = []
    vertical_circular_end_blind_slot_site1 = []
    vertical_circular_end_blind_slot_site2 = []
    vertical_circular_end_blind_slot_site3 = []
    vertical_circular_end_blind_slot_site4 = []
    for i in range(0, len(vertical_circular_end_blind_slot_normal_korr)):
        if vertical_circular_end_blind_slot_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = vertical_circular_end_blind_slot_normal_korr[i] + [i]
            vertical_circular_end_blind_slot_top.append(a)
        if vertical_circular_end_blind_slot_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = vertical_circular_end_blind_slot_normal_korr[i] + [i]
            vertical_circular_end_blind_slot_site1.append(a)
        if vertical_circular_end_blind_slot_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = vertical_circular_end_blind_slot_normal_korr[i] + [i]
            vertical_circular_end_blind_slot_site2.append(a)
        if vertical_circular_end_blind_slot_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = vertical_circular_end_blind_slot_normal_korr[i] + [i]
            vertical_circular_end_blind_slot_site3.append(a)
        if vertical_circular_end_blind_slot_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = vertical_circular_end_blind_slot_normal_korr[i] + [i]
            vertical_circular_end_blind_slot_site4.append(a)

    vertical_circular_end_blind_slot_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    vertical_circular_end_blind_slot_operation_normal_list = [vertical_circular_end_blind_slot_top, vertical_circular_end_blind_slot_site1,
                                                 vertical_circular_end_blind_slot_site2, vertical_circular_end_blind_slot_site3,
                                                 vertical_circular_end_blind_slot_site4]
    vertical_circular_end_blind_slot_operation_dict = dict(
        zip(vertical_circular_end_blind_slot_operation_face_list, vertical_circular_end_blind_slot_operation_normal_list))
# horizontal_circular_end_blind_slot
if 21.0 in dict_all:
    horizontal_circular_end_blind_slot_normal = []
    for i in range(0, len(horizontal_circular_end_blind_slot_face_line)):
        horizontal_circular_end_blind_slot_face = App.ActiveDocument.Common.Shape.Faces[
            int(horizontal_circular_end_blind_slot_face_line[i][0] - 1)]
        horizontal_circular_end_blind_slot_face_normal = horizontal_circular_end_blind_slot_face.normalAt(0, 0)
        horizontal_circular_end_blind_slot_normal.append(list(horizontal_circular_end_blind_slot_face_normal))

    horizontal_circular_end_blind_slot_normal_korr = []
    for i in range(0, len(horizontal_circular_end_blind_slot_normal)):
        rep = [0.0 if x == -0.0 else x for x in horizontal_circular_end_blind_slot_normal[i]]
        horizontal_circular_end_blind_slot_normal_korr.append(rep)

    horizontal_circular_end_blind_slot_top = []
    horizontal_circular_end_blind_slot_site1 = []
    horizontal_circular_end_blind_slot_site2 = []
    horizontal_circular_end_blind_slot_site3 = []
    horizontal_circular_end_blind_slot_site4 = []
    for i in range(0, len(horizontal_circular_end_blind_slot_normal_korr)):
        if horizontal_circular_end_blind_slot_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = horizontal_circular_end_blind_slot_normal_korr[i] + [i]
            horizontal_circular_end_blind_slot_top.append(a)
        if horizontal_circular_end_blind_slot_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = horizontal_circular_end_blind_slot_normal_korr[i] + [i]
            horizontal_circular_end_blind_slot_site1.append(a)
        if horizontal_circular_end_blind_slot_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = horizontal_circular_end_blind_slot_normal_korr[i] + [i]
            horizontal_circular_end_blind_slot_site2.append(a)
        if horizontal_circular_end_blind_slot_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = horizontal_circular_end_blind_slot_normal_korr[i] + [i]
            horizontal_circular_end_blind_slot_site3.append(a)
        if horizontal_circular_end_blind_slot_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = horizontal_circular_end_blind_slot_normal_korr[i] + [i]
            horizontal_circular_end_blind_slot_site4.append(a)
    horizontal_circular_end_blind_slot_operation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    horizontal_circular_end_blind_slot_operation_normal_list = [horizontal_circular_end_blind_slot_top, horizontal_circular_end_blind_slot_site1,
                                                 horizontal_circular_end_blind_slot_site2, horizontal_circular_end_blind_slot_site3,
                                                 horizontal_circular_end_blind_slot_site4]
    horizontal_circular_end_blind_slot_operation_dict = dict(
        zip(horizontal_circular_end_blind_slot_operation_face_list, horizontal_circular_end_blind_slot_operation_normal_list))
# six_sides_pocket
if 23.0 in dict_all:
    six_sides_pocket_normal = []
    for i in range(0, len(six_sides_pocket_face_line)):
        six_sides_pocket_face = App.ActiveDocument.Common.Shape.Faces[int(six_sides_pocket_face_line[i][0] - 1)]
        six_sides_pocket_face_normal = six_sides_pocket_face.normalAt(0, 0)
        six_sides_pocket_normal.append(list(six_sides_pocket_face_normal))

    six_sides_pocket_normal_korr = []
    for i in range(0, len(six_sides_pocket_normal)):
        rep = [0.0 if x == -0.0 else x for x in six_sides_pocket_normal[i]]
        six_sides_pocket_normal_korr.append(rep)

    six_sides_pocket_top = []
    six_sides_pocket_site1 = []
    six_sides_pocket_site2 = []
    six_sides_pocket_site3 = []
    six_sides_pocket_site4 = []
    for i in range(0, len(six_sides_pocket_normal_korr)):
        if six_sides_pocket_normal_korr[i] == [0.0, 0.0, 1.0]:
            a = six_sides_pocket_normal_korr[i] + [i]
            six_sides_pocket_top.append(a)
        if six_sides_pocket_normal_korr[i] == [-1.0, 0.0, 0.0]:
            a = six_sides_pocket_normal_korr[i] + [i]
            six_sides_pocket_site1.append(a)
        if six_sides_pocket_normal_korr[i] == [0.0, 1.0, 0.0]:
            a = six_sides_pocket_normal_korr[i] + [i]
            six_sides_pocket_site2.append(a)
        if six_sides_pocket_normal_korr[i] == [1.0, 0.0, 0.0]:
            a = six_sides_pocket_normal_korr[i] + [i]
            six_sides_pocket_site3.append(a)
        if six_sides_pocket_normal_korr[i] == [0.0, -1.0, 0.0]:
            a = six_sides_pocket_normal_korr[i] + [i]
            six_sides_pocket_site4.append(a)

    six_sides_pocketoperation_face_list = ['Top', 'Site1', 'Site2', 'Site3', 'Site4']
    six_sides_pocket_operation_normal_list = [six_sides_pocket_top, six_sides_pocket_site1,
                                                   six_sides_pocket_site2, six_sides_pocket_site3, six_sides_pocket_site4]
    six_sides_pocket_operation_dict = dict(zip(six_sides_pocket_operation_face_list, six_sides_pocket_operation_normal_list))
App.closeDocument("Common")

'''Reale Modelldatei öffnen (model.FCStd)'''
DOC=App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
obj = App.ActiveDocument.getObject(file_name_2)
face_anzahl_list = obj.Shape.Faces

xmin = obj.Shape.BoundBox.XMin
xmax = obj.Shape.BoundBox.XMax
ymin = obj.Shape.BoundBox.YMin
ymax = obj.Shape.BoundBox.YMax
zmin = obj.Shape.BoundBox.ZMin
zmax = obj.Shape.BoundBox.ZMax
centervector = ((xmin+xmax)/2,(ymin+ymax)/2,(zmin+zmax)/2) #Die Drehachse berechnen

'''Verbindet die Unterseite des Merkmals mit dem Gesicht des Originalmodells anhand der Schwerpunktkoordinaten.'''
face_centermass_list = [] #Mittelpunkte aller Flächen des ursprünglichen Modells
for i in range(0,len(face_anzahl_list)):
    face_centermass_face = App.ActiveDocument.Solid.Shape.Faces[i]
    face_centermass = face_centermass_face.CenterOfMass
    face_centermass_list.append(list(face_centermass))
if 10.0 in dict_all:
    bottom_face_line_original = []
    for j in range(0, len(pocket_centermass_list)):
        a = face_centermass_list.index(pocket_centermass_list[j])
        bottom_face_line_original.append([a + 1])
if 2.0 in dict_all:
    blind_hole_bottom_face_line_original = []
    for j in range(0, len(blind_hole_centermass_list)):
        a = face_centermass_list.index(blind_hole_centermass_list[j])
        blind_hole_bottom_face_line_original.append([a + 1])
if 14.0 in dict_all:
    blind_step_bottom_face_line_original = []
    for j in range(0, len(blind_step_centermass_list)):
        a = face_centermass_list.index(blind_step_centermass_list[j])
        blind_step_bottom_face_line_original.append([a + 1])
if 7.0 in dict_all:
    rechtgular_through_slot_bottom_face_line_original= []
    for j in range(0, len(rechtgular_through_slot_centermass_list)):
        a = face_centermass_list.index(rechtgular_through_slot_centermass_list[j])
        rechtgular_through_slot_bottom_face_line_original.append([a + 1])
if 8.0 in dict_all:
    rechtgular_blind_slot_bottom_face_line_original = []
    for j in range(0, len(rechtgular_blind_slot_centermass_list)):
        a = face_centermass_list.index(rechtgular_blind_slot_centermass_list[j])
        rechtgular_blind_slot_bottom_face_line_original.append([a + 1])
if 9.0 in dict_all:
    triangular_pocket_bottom_face_line_original = []
    for j in range(0, len(triangular_pocket_centermass_list)):
        a = face_centermass_list.index(triangular_pocket_centermass_list[j])
        triangular_pocket_bottom_face_line_original.append([a + 1])
if 12.0 in dict_all:
    triangular_blind_step_bottom_face_line_original = []
    for j in range(0, len(triangular_blind_step_centermass_list)):
        a = face_centermass_list.index(triangular_blind_step_centermass_list[j])
        triangular_blind_step_bottom_face_line_original.append([a + 1])
if 13.0 in dict_all:
    circular_blind_step_bottom_face_line_original = []
    for j in range(0, len(circular_blind_step_centermass_list)):
        a = face_centermass_list.index(circular_blind_step_centermass_list[j])
        circular_blind_step_bottom_face_line_original.append([a + 1])
if 15.0 in dict_all:
    rechtangular_through_step_bottom_face_line_original = []
    for j in range(0, len(rechtangular_through_step_centermass_list)):
        a = face_centermass_list.index(rechtangular_through_step_centermass_list[j])
        rechtangular_through_step_bottom_face_line_original.append([a + 1])
if 17.0 in dict_all:
    slanted_through_step_bottom_face_line_original= []
    for j in range(0, len(slanted_through_step_centermass_list)):
        a = face_centermass_list.index(slanted_through_step_centermass_list[j])
        slanted_through_step_bottom_face_line_original.append([a + 1])
if 20.0 in dict_all:
    vertical_circular_end_blind_slot_bottom_face_line_original = []
    for j in range(0, len(vertical_circular_end_blind_slot_centermass_list)):
        a = face_centermass_list.index(vertical_circular_end_blind_slot_centermass_list[j])
        vertical_circular_end_blind_slot_bottom_face_line_original.append([a + 1])
if 21.0 in dict_all:
    horizontal_circular_end_blind_slot_bottom_face_line_original = []
    for j in range(0,len(horizontal_circular_end_blind_slot_centermass_list)):
        a = face_centermass_list.index(horizontal_circular_end_blind_slot_centermass_list[j])
        horizontal_circular_end_blind_slot_bottom_face_line_original.append([a+1])
if 23.0 in dict_all:
    six_sides_pocket_bottom_face_line_original = []
    for j in range(0, len(six_sides_pocket_centermass_list)):
        a = face_centermass_list.index(six_sides_pocket_centermass_list[j])
        six_sides_pocket_bottom_face_line_original.append([a + 1])
'''Das Modell auswählen, das bearbeitet werden soll'''
Part1 =  DOC.getObject(file_name_2)
'''operation definition (Werkzeug und Operation)'''
def werkzeug(toolpath,name2,horizrapid = "15mm/s",vertrapid = "2mm/s",horizfeed="10mm/s",vertfeed ="10mm/s"):
    name1 = PathToolBit.Declaration(toolpath)

    tool = PathToolController.Create(name2)
    tool.setExpression('HorizRapid', None)
    tool.HorizRapid = horizrapid
    tool.setExpression('VertRapid', None)
    tool.VertRapid = vertrapid
    tool.setExpression('HorizFeed', None)
    tool.VertRapid = horizfeed
    tool.setExpression('VertFeed', None)
    tool.VertRapid = vertfeed



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

def adaptive_operation(facName, use_outline, werkzeugname, finishing_profile = 0,stepdown = 1, force_inside_out = 1,helixangle = 5,
                       helixconeangle = 0,helixdiameterlimit = 0, keeptooldownratio = 3,
                       liftdistance = 0 ,operation_type = 0, si_de = 0, stepover = 20 ,stocktoleave = 0,
                       tolerance = 0.1 ,use_helix_arcs = 1 , finishdepth = 0, name = 0):
    adaptive = PathAdaptive.Create('Adaptive%d'%(name))
    adaptive.Base = (Part1,facName)

    finishingprofile = ['true' , '']
    adaptive.FinishingProfile = bool(finishingprofile[finishing_profile])


    forceinsideout = ['true','']
    adaptive.ForceInsideOut = bool(forceinsideout[force_inside_out])

    adaptive.setExpression('HelixAngle',None)
    adaptive.HelixAngle = helixangle

    adaptive.setExpression('HelixConeAngle',None)
    adaptive.HelixConeAngle = helixconeangle

    adaptive.setExpression('HelixDiameterLimit',None)
    adaptive.HelixDiameterLimit = helixdiameterlimit

    adaptive.setExpression('KeepToolDownRatio',None)
    adaptive.KeepToolDownRatio = keeptooldownratio

    adaptive.setExpression('LiftDistance',None)
    adaptive.LiftDistance = liftdistance

    operationtype = ['Clearing','Profiling']
    adaptive.OperationType = operationtype[operation_type]

    side = ['Inside','Outside']
    adaptive.Side = side[si_de]

    adaptive.setExpression('StepOver',None)
    adaptive.StepOver = stepover

    adaptive.setExpression('StockToLeave',None)
    adaptive.StockToLeave = stocktoleave

    adaptive.setExpression('Tolerance',None)
    adaptive.Tolerance = tolerance

    usehelixarcs = ['true','']
    adaptive.UseHelixArcs = bool(usehelixarcs[use_helix_arcs])

    useoutline = ['true','']
    adaptive.UseOutline = bool(useoutline[use_outline])

    adaptive.setExpression('FinishDepth',None)
    adaptive.FinishDepth = finishdepth

    adaptive.setExpression('StepDown',None)
    adaptive.StepDown = stepdown

    Gui.Selection.addSelection(file_name_1, 'Adaptive%d'%(name))
    App.getDocument(file_name_1).getObject('Adaptive%d'%(name)).ToolController = App.getDocument(file_name_1).getObject(werkzeugname)

    DOC.recompute()


'''Operation Bearbeitung'''
# Schritt1: top face bearbeitung
# Job erstellen
Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job_top', [Part1], None)
job.ViewObject.Proxy = PathJobGui.ViewProvider(job.ViewObject)
# Einstellung über Stock
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
# Werkzeug Aufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
App.getDocument(file_name_1).getObject('ToolBit002').ShapeName = "ballend"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
auswahl_werkzeug = werkzeuglist[0]

# Bearbeitung Durchführung
if 10.0 in dict_all:
    for i in range (0,len(pocket_operation_dict['Top'])):
        top_pocket_face_id = bottom_face_line_original[pocket_operation_dict['Top'][i][3]]
        top_pocket_face = 'Face{:d}'.format(top_pocket_face_id[0])
        adaptive_operation(top_pocket_face,0,auswahl_werkzeug,0,name=i)
if 2.0 in dict_all:
    for i in range (0,len(blind_hole_operation_dict['Top'])):
        top_blind_hole_face_id = blind_hole_bottom_face_line_original[blind_hole_operation_dict['Top'][i][3]]
        top_blind_hole_face = 'Face{:d}'.format(top_blind_hole_face_id[0])
        adaptive_operation(top_blind_hole_face, 0, auswahl_werkzeug, 0, name=i+10)
if 14.0 in dict_all:
    for i in range (0,len(blind_step_operation_dict['Top'])):
        top_blind_step_face_id = blind_step_bottom_face_line_original[blind_step_operation_dict['Top'][i][3]]
        top_blind_step_face = 'Face{:d}'.format(top_blind_step_face_id[0])
        adaptive_operation(top_blind_step_face, 0, auswahl_werkzeug, 0, name=i + 20)
if 7.0 in dict_all:
    for i in range (0,len(rechtgular_through_slot_operation_dict['Top'])):
        top_rechtgular_through_slot_face_id = rechtgular_through_slot_bottom_face_line_original[rechtgular_through_slot_operation_dict['Top'][i][3]]
        top_rechtgular_through_slot_face = 'Face{:d}'.format(top_rechtgular_through_slot_face_id[0])
        adaptive_operation(top_rechtgular_through_slot_face,0,auswahl_werkzeug,0,name=i + 30)
if 8.0 in dict_all:
    for i in range (0,len(rechtgular_blind_slot_operation_dict['Top'])):
        top_rechtgular_blind_slot_face_id = rechtgular_blind_slot_bottom_face_line_original[rechtgular_blind_slot_operation_dict['Top'][i][3]]
        top_rechtgular_blind_slot_face = 'Face{:d}'.format(top_rechtgular_blind_slot_face_id[0])
        adaptive_operation(top_rechtgular_blind_slot_face,0,auswahl_werkzeug,0,name=i + 40)
if 9.0 in dict_all:
    for i in range (0,len(triangular_pocket_operation_dict['Top'])):
        top_triangular_pocket_face_id = triangular_pocket_bottom_face_line_original[triangular_pocket_operation_dict['Top'][i][3]]
        top_triangular_pocket_face = 'Face{:d}'.format(top_triangular_pocket_face_id[0])
        adaptive_operation(top_triangular_pocket_face,0,auswahl_werkzeug,0,name=i + 50)
if 12.0 in dict_all:
    for i in range (0,len(triangular_blind_step_operation_dict['Top'])):
        top_triangular_blind_step_face_id = triangular_blind_step_bottom_face_line_original[triangular_blind_step_operation_dict['Top'][i][3]]
        top_triangular_blind_step_face = 'Face{:d}'.format(top_triangular_blind_step_face_id[0])
        adaptive_operation(top_triangular_blind_step_face,0,auswahl_werkzeug,0,name=i +60)
if 13.0 in dict_all:
    for i in range (0,len(circular_blind_step_operation_dict['Top'])):
        top_circular_blind_step_face_id = circular_blind_step_bottom_face_line_original[circular_blind_step_operation_dict['Top'][i][3]]
        top_circular_blind_step_face = 'Face{:d}'.format(top_circular_blind_step_face_id[0])
        adaptive_operation(top_circular_blind_step_face,0,auswahl_werkzeug,0,name=i+70)
if 15.0 in dict_all:
    for i in range (0,len(rechtangular_through_step_operation_dict['Top'])):
        top_rechtangular_through_step_face_id = rechtangular_through_step_bottom_face_line_original[rechtangular_through_step_operation_dict['Top'][i][3]]
        top_rechtangular_through_step_face = 'Face{:d}'.format(top_rechtangular_through_step_face_id[0])
        adaptive_operation(top_rechtangular_through_step_face,0,auswahl_werkzeug,0,name=i+80)
if 17.0 in dict_all:
    for i in range (0,len(slanted_through_step_operation_dict['Top'])):
        top_slanted_through_step_face_id = slanted_through_step_bottom_face_line_original[slanted_through_step_operation_dict['Top'][i][3]]
        top_slanted_through_step_face = 'Face{:d}'.format(top_slanted_through_step_face_id[0])
        adaptive_operation(top_slanted_through_step_face,0,auswahl_werkzeug,0,name=i+90)
if 20.0 in dict_all:
    for i in range (0,len(vertical_circular_end_blind_slot_operation_dict['Top'])):
        top_vertical_circular_end_blind_slot_face_id = vertical_circular_end_blind_slot_bottom_face_line_original[vertical_circular_end_blind_slot_operation_dict['Top'][i][3]]
        top_vertical_circular_end_blind_slot_face = 'Face{:d}'.format(top_vertical_circular_end_blind_slot_face_id[0])
        adaptive_operation(top_vertical_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+100)
if 21.0 in dict_all:
    for i in range (0,len(horizontal_circular_end_blind_slot_operation_dict['Top'])):
        top_horizontal_circular_end_blind_slot_face_id = horizontal_circular_end_blind_slot_bottom_face_line_original[horizontal_circular_end_blind_slot_operation_dict['Top'][i][3]]
        top_horizontal_circular_end_blind_slot_face = 'Face{:d}'.format(top_horizontal_circular_end_blind_slot_face_id[0])
        adaptive_operation(top_horizontal_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+110)
if 23.0 in dict_all:
    for i in range (0,len(six_sides_pocket_operation_dict['Top'])):
        top_six_sides_pocket_face_id = six_sides_pocket_bottom_face_line_original[six_sides_pocket_operation_dict['Top'][i][3]]
        top_six_sides_pocket_face = 'Face{:d}'.format(top_six_sides_pocket_face_id[0])
        adaptive_operation(top_six_sides_pocket_face,0,auswahl_werkzeug,0,name=i+120)

# G-Code ausgeben
job.PostProcessorOutputFile = gcodePath_top
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
gcode = post.export(postlist, gcodePath_top , job.PostProcessorArgs)
DOC.recompute()
print("--- done ---")
App.closeDocument(file_name_1)


# Schritt2: site1 operation
DOC=App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
Part1 =  DOC.getObject(file_name_2)

obj = App.ActiveDocument.Solid
rot = App.Rotation(App.Vector(0,1,0),90) # 90 Grad um Y-Achse
centre = App.Vector(centervector) # zentraler Punkt der Box
pos = obj.Placement.Base  # Position Punkt der Box
newplace = App.Placement(pos,rot,centre) # ein neues Placement-Objekt erstellen
obj.Placement = newplace

# Job erstellen
Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job_site1', [Part1], None)
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

# Werkzeug Aufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
auswahl_werkzeug = werkzeuglist[0]
#operation
if 10.0 in dict_all:
    for i in range (0,len(pocket_operation_dict['Site1'])):
        site1_pocket_face_id = bottom_face_line_original[pocket_operation_dict['Site1'][i][3]]
        site1_pocket_face = 'Face{:d}'.format(site1_pocket_face_id[0])
        adaptive_operation(site1_pocket_face,0,auswahl_werkzeug,0,name=i)
if 2.0 in dict_all:
    for i in range (0,len(blind_hole_operation_dict['Site1'])):
        site1_blind_hole_face_id = blind_hole_bottom_face_line_original[blind_hole_operation_dict['Site1'][i][3]]
        site1_blind_hole_face = 'Face{:d}'.format(site1_blind_hole_face_id[0])
        adaptive_operation(site1_blind_hole_face, 0, auswahl_werkzeug, 0, name=i+10)
if 14.0 in dict_all:
    for i in range (0,len(blind_step_operation_dict['Site1'])):
        site1_blind_step_face_id = blind_step_bottom_face_line_original[blind_step_operation_dict['Site1'][i][3]]
        site1_blind_step_face = 'Face{:d}'.format(site1_blind_step_face_id[0])
        adaptive_operation(site1_blind_step_face, 0, auswahl_werkzeug, 0, name=i + 20)
if 7.0 in dict_all:
    for i in range (0,len(rechtgular_through_slot_operation_dict['Site1'])):
        site1_rechtgular_through_slot_face_id = rechtgular_through_slot_bottom_face_line_original[rechtgular_through_slot_operation_dict['Site1'][i][3]]
        site1_rechtgular_through_slot_face = 'Face{:d}'.format(site1_rechtgular_through_slot_face_id[0])
        adaptive_operation(site1_rechtgular_through_slot_face,0,auswahl_werkzeug,0,name=i+30)
if 8.0 in dict_all:
    for i in range (0,len(rechtgular_blind_slot_operation_dict['Site1'])):
        site1_rechtgular_blind_slot_face_id = rechtgular_blind_slot_bottom_face_line_original[rechtgular_blind_slot_operation_dict['Site1'][i][3]]
        site1_rechtgular_blind_slot_face = 'Face{:d}'.format(site1_rechtgular_blind_slot_face_id[0])
        adaptive_operation(site1_rechtgular_blind_slot_face,0,auswahl_werkzeug,0,name=i+40)
if 9.0 in dict_all:
    for i in range (0,len(triangular_pocket_operation_dict['Site1'])):
        site1_triangular_pocket_face_id = triangular_pocket_bottom_face_line_original[triangular_pocket_operation_dict['Site1'][i][3]]
        site1_triangular_pocket_face = 'Face{:d}'.format(site1_triangular_pocket_face_id[0])
        adaptive_operation(site1_triangular_pocket_face,0,auswahl_werkzeug,0,name=i+50)
if 12.0 in dict_all:
    for i in range (0,len(triangular_blind_step_operation_dict['Site1'])):
        site1_triangular_blind_step_face_id = triangular_blind_step_bottom_face_line_original[triangular_blind_step_operation_dict['Site1'][i][3]]
        site1_triangular_blind_step_face = 'Face{:d}'.format(site1_triangular_blind_step_face_id[0])
        adaptive_operation(site1_triangular_blind_step_face,0,auswahl_werkzeug,0,name=i+60)
if 13.0 in dict_all:
    for i in range (0,len(circular_blind_step_operation_dict['Site1'])):
        site1_circular_blind_step_face_id = circular_blind_step_bottom_face_line_original[circular_blind_step_operation_dict['Site1'][i][3]]
        site1_circular_blind_step_face = 'Face{:d}'.format(site1_circular_blind_step_face_id[0])
        adaptive_operation(site1_circular_blind_step_face,0,auswahl_werkzeug,0,name=i+70)
if 15.0 in dict_all:
    for i in range (0,len(rechtangular_through_step_operation_dict['Site1'])):
        site1_rechtangular_through_step_face_id = rechtangular_through_step_bottom_face_line_original[rechtangular_through_step_operation_dict['Site1'][i][3]]
        site1_rechtangular_through_step_face = 'Face{:d}'.format(site1_rechtangular_through_step_face_id[0])
        adaptive_operation(site1_rechtangular_through_step_face,0,auswahl_werkzeug,0,name=i+80)
if 17.0 in dict_all:
    for i in range (0,len(slanted_through_step_operation_dict['Site1'])):
        site1_slanted_through_step_face_id = slanted_through_step_bottom_face_line_original[slanted_through_step_operation_dict['Site1'][i][3]]
        site1_slanted_through_step_face = 'Face{:d}'.format(site1_slanted_through_step_face_id[0])
        adaptive_operation(site1_slanted_through_step_face,0,auswahl_werkzeug,0,name=i+90)
if 20.0 in dict_all:
    for i in range (0,len(vertical_circular_end_blind_slot_operation_dict['Site1'])):
        site1_vertical_circular_end_blind_slot_face_id = vertical_circular_end_blind_slot_bottom_face_line_original[vertical_circular_end_blind_slot_operation_dict['Site1'][i][3]]
        site1_vertical_circular_end_blind_slot_face = 'Face{:d}'.format(site1_vertical_circular_end_blind_slot_face_id[0])
        adaptive_operation(site1_vertical_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+100)
if 21.0 in dict_all:
    for i in range (0,len(horizontal_circular_end_blind_slot_operation_dict['Site1'])):
        site1_horizontal_circular_end_blind_slot_face_id = horizontal_circular_end_blind_slot_bottom_face_line_original[horizontal_circular_end_blind_slot_operation_dict['Site1'][i][3]]
        site1_horizontal_circular_end_blind_slot_face = 'Face{:d}'.format(site1_horizontal_circular_end_blind_slot_face_id[0])
        adaptive_operation(site1_horizontal_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+110)
if 23.0 in dict_all:
    for i in range (0,len(six_sides_pocket_operation_dict['Site1'])):
        site1_six_sides_pocket_face_id = six_sides_pocket_bottom_face_line_original[six_sides_pocket_operation_dict['Site1'][i][3]]
        site1_six_sides_pocket_face = 'Face{:d}'.format(site1_six_sides_pocket_face_id[0])
        adaptive_operation(site1_six_sides_pocket_face,0,auswahl_werkzeug,0,name=i+120)

job.PostProcessorOutputFile = gcodePath_site1
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
gcode = post.export(postlist, gcodePath_site1, job.PostProcessorArgs)
DOC.recompute()
print("--- done ---")
App.closeDocument(file_name_1)

# Schritt3: Site2 operation
DOC = App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
Part1 = DOC.getObject(file_name_2)

obj = App.ActiveDocument.Solid
rot = App.Rotation(App.Vector(1,0,0),90)
centre = App.Vector(centervector)
pos = obj.Placement.Base
newplace = App.Placement(pos,rot,centre)
obj.Placement = newplace

Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job_site2', [Part1], None)
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

#Werkzeug Aufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
auswahl_werkzeug = werkzeuglist[0]
#operation
if 10.0 in dict_all:
    for i in range (0,len(pocket_operation_dict['Site2'])):
        site2_pocket_face_id = bottom_face_line_original[pocket_operation_dict['Site2'][i][3]]
        site2_pocket_face = 'Face{:d}'.format(site2_pocket_face_id[0])
        adaptive_operation(site2_pocket_face,0,auswahl_werkzeug,0,name=i)
if 2.0 in dict_all:
    for i in range (0,len(blind_hole_operation_dict['Site2'])):
        site2_blind_hole_face_id = blind_hole_bottom_face_line_original[blind_hole_operation_dict['Site2'][i][3]]
        site2_blind_hole_face = 'Face{:d}'.format(site2_blind_hole_face_id[0])
        adaptive_operation(site2_blind_hole_face, 0, auswahl_werkzeug, 0, name=i+10)
if 14.0 in dict_all:
    for i in range (0,len(blind_step_operation_dict['Site2'])):
        site2_blind_step_face_id = blind_step_bottom_face_line_original[blind_step_operation_dict['Site2'][i][3]]
        site2_blind_step_face = 'Face{:d}'.format(site2_blind_step_face_id[0])
        adaptive_operation(site2_blind_step_face, 0, auswahl_werkzeug, 0, name=i + 20)
if 7.0 in dict_all:
    for i in range (0,len(rechtgular_through_slot_operation_dict['Site2'])):
        site2_rechtgular_through_slot_face_id = rechtgular_through_slot_bottom_face_line_original[rechtgular_through_slot_operation_dict['Site2'][i][3]]
        site2_rechtgular_through_slot_face = 'Face{:d}'.format(site2_rechtgular_through_slot_face_id[0])
        adaptive_operation(site2_rechtgular_through_slot_face,0,auswahl_werkzeug,0,name=i+30)
if 8.0 in dict_all:
    for i in range (0,len(rechtgular_blind_slot_operation_dict['Site2'])):
        site2_rechtgular_blind_slot_face_id = rechtgular_blind_slot_bottom_face_line_original[rechtgular_blind_slot_operation_dict['Site2'][i][3]]
        site2_rechtgular_blind_slot_face = 'Face{:d}'.format(site2_rechtgular_blind_slot_face_id[0])
        adaptive_operation(site2_rechtgular_blind_slot_face,0,auswahl_werkzeug,0,name=i+40)
if 9.0 in dict_all:
    for i in range (0,len(triangular_pocket_operation_dict['Site2'])):
        site2_triangular_pocket_face_id = triangular_pocket_bottom_face_line_original[triangular_pocket_operation_dict['Site2'][i][3]]
        site2_triangular_pocket_face = 'Face{:d}'.format(site2_triangular_pocket_face_id[0])
        adaptive_operation(site2_triangular_pocket_face,0,auswahl_werkzeug,0,name=i+50)
if 12.0 in dict_all:
    for i in range (0,len(triangular_blind_step_operation_dict['Site2'])):
        site2_triangular_blind_step_face_id = triangular_blind_step_bottom_face_line_original[triangular_blind_step_operation_dict['Site2'][i][3]]
        site2_triangular_blind_step_face = 'Face{:d}'.format(site2_triangular_blind_step_face_id[0])
        adaptive_operation(site2_triangular_blind_step_face,0,auswahl_werkzeug,0,name=i+60)
if 13.0 in dict_all:
    for i in range (0,len(circular_blind_step_operation_dict['Site2'])):
        site2_circular_blind_step_face_id = circular_blind_step_bottom_face_line_original[circular_blind_step_operation_dict['Site2'][i][3]]
        site2_circular_blind_step_face = 'Face{:d}'.format(site2_circular_blind_step_face_id[0])
        adaptive_operation(site2_circular_blind_step_face,0,auswahl_werkzeug,0,name=i+70)
if 15.0 in dict_all:
    for i in range (0,len(rechtangular_through_step_operation_dict['Site2'])):
        site2_rechtangular_through_step_face_id = rechtangular_through_step_bottom_face_line_original[rechtangular_through_step_operation_dict['Site2'][i][3]]
        site2_rechtangular_through_step_face = 'Face{:d}'.format(site2_rechtangular_through_step_face_id[0])
        adaptive_operation(site2_rechtangular_through_step_face,0,auswahl_werkzeug,0,name=i+80)
if 17.0 in dict_all:
    for i in range (0,len(slanted_through_step_operation_dict['Site2'])):
        site2_slanted_through_step_face_id = slanted_through_step_bottom_face_line_original[slanted_through_step_operation_dict['Site2'][i][3]]
        site2_slanted_through_step_face = 'Face{:d}'.format(site2_slanted_through_step_face_id[0])
        adaptive_operation(site2_slanted_through_step_face,0,auswahl_werkzeug,0,name=i+90)
if 20.0 in dict_all:
    for i in range (0,len(vertical_circular_end_blind_slot_operation_dict['Site2'])):
        site2_vertical_circular_end_blind_slot_face_id = vertical_circular_end_blind_slot_bottom_face_line_original[vertical_circular_end_blind_slot_operation_dict['Site2'][i][3]]
        site2_vertical_circular_end_blind_slot_face = 'Face{:d}'.format(site2_vertical_circular_end_blind_slot_face_id[0])
        adaptive_operation(site2_vertical_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+100)
if 21.0 in dict_all:
    for i in range (0,len(horizontal_circular_end_blind_slot_operation_dict['Site2'])):
        site2_horizontal_circular_end_blind_slot_face_id = horizontal_circular_end_blind_slot_bottom_face_line_original[horizontal_circular_end_blind_slot_operation_dict['Site2'][i][3]]
        site2_horizontal_circular_end_blind_slot_face = 'Face{:d}'.format(site2_horizontal_circular_end_blind_slot_face_id[0])
        adaptive_operation(site2_horizontal_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+110)
if 23.0 in dict_all:
    for i in range (0,len(six_sides_pocket_operation_dict['Site2'])):
        site2_six_sides_pocket_face_id = six_sides_pocket_bottom_face_line_original[six_sides_pocket_operation_dict['Site2'][i][3]]
        site2_six_sides_pocket_face = 'Face{:d}'.format(site2_six_sides_pocket_face_id[0])
        adaptive_operation(site2_six_sides_pocket_face,0,auswahl_werkzeug,0,name=i+120)

job.PostProcessorOutputFile = gcodePath_site2
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
gcode = post.export(postlist, gcodePath_site2, job.PostProcessorArgs)
DOC.recompute()
print("--- done ---")
App.closeDocument(file_name_1)


# Schritt4: site3 operation
DOC = App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()

obj = App.ActiveDocument.Solid
rot = App.Rotation(App.Vector(0,1,0),-90)
centre = App.Vector(centervector)
pos = obj.Placement.Base
newplace = App.Placement(pos,rot,centre)
obj.Placement = newplace
Part1 = DOC.getObject(file_name_2)

Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job_top', [Part1], None)
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

#Werkzeug Aufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
auswahl_werkzeug = werkzeuglist[0]
#operation
if 10.0 in dict_all:
    for i in range (0,len(pocket_operation_dict['Site3'])):
        site3_pocket_face_id = bottom_face_line_original[pocket_operation_dict['Site3'][i][3]]
        site3_pocket_face = 'Face{:d}'.format(site3_pocket_face_id[0])
        adaptive_operation(site3_pocket_face,0,auswahl_werkzeug,0,name=i)
if 2.0 in dict_all:
    for i in range (0,len(blind_hole_operation_dict['Site3'])):
        site3_blind_hole_face_id = blind_hole_bottom_face_line_original[blind_hole_operation_dict['Site3'][i][3]]
        site3_blind_hole_face = 'Face{:d}'.format(site3_blind_hole_face_id[0])
        adaptive_operation(site3_blind_hole_face, 0, auswahl_werkzeug, 0, name=i+10)
if 14.0 in dict_all:
    for i in range (0,len(blind_step_operation_dict['Site3'])):
        site3_blind_step_face_id = blind_step_bottom_face_line_original[blind_step_operation_dict['Site3'][i][3]]
        site3_blind_step_face = 'Face{:d}'.format(site3_blind_step_face_id[0])
        adaptive_operation(site3_blind_step_face, 0, auswahl_werkzeug, 0, name=i + 20)
if 7.0 in dict_all:
    for i in range (0,len(rechtgular_through_slot_operation_dict['Site3'])):
        site3_rechtgular_through_slot_face_id = rechtgular_through_slot_bottom_face_line_original[rechtgular_through_slot_operation_dict['Site3'][i][3]]
        site3_rechtgular_through_slot_face = 'Face{:d}'.format(site3_rechtgular_through_slot_face_id[0])
        adaptive_operation(site3_rechtgular_through_slot_face,0,auswahl_werkzeug,0,name=i+30)
if 8.0 in dict_all:
    for i in range (0,len(rechtgular_blind_slot_operation_dict['Site3'])):
        site3_rechtgular_blind_slot_face_id = rechtgular_blind_slot_bottom_face_line_original[rechtgular_blind_slot_operation_dict['Site3'][i][3]]
        site3_rechtgular_blind_slot_face = 'Face{:d}'.format(site3_rechtgular_blind_slot_face_id[0])
        adaptive_operation(site3_rechtgular_blind_slot_face,0,auswahl_werkzeug,0,name=i+40)
if 9.0 in dict_all:
    for i in range (0,len(triangular_pocket_operation_dict['Site3'])):
        site3_triangular_pocket_face_id = triangular_pocket_bottom_face_line_original[triangular_pocket_operation_dict['Site3'][i][3]]
        site3_triangular_pocket_face = 'Face{:d}'.format(site3_triangular_pocket_face_id[0])
        adaptive_operation(site3_triangular_pocket_face,0,auswahl_werkzeug,0,name=i+50)
if 12.0 in dict_all:
    for i in range (0,len(triangular_blind_step_operation_dict['Site3'])):
        site3_triangular_blind_step_face_id = triangular_blind_step_bottom_face_line_original[triangular_blind_step_operation_dict['Site3'][i][3]]
        site3_triangular_blind_step_face = 'Face{:d}'.format(site3_triangular_blind_step_face_id[0])
        adaptive_operation(site3_triangular_blind_step_face,0,auswahl_werkzeug,0,name=i+60)
if 13.0 in dict_all:
    for i in range (0,len(circular_blind_step_operation_dict['Site3'])):
        site3_circular_blind_step_face_id = circular_blind_step_bottom_face_line_original[circular_blind_step_operation_dict['Site3'][i][3]]
        site3_circular_blind_step_face = 'Face{:d}'.format(site3_circular_blind_step_face_id[0])
        adaptive_operation(site3_circular_blind_step_face,0,auswahl_werkzeug,0,name=i+70)
if 15.0 in dict_all:
    for i in range (0,len(rechtangular_through_step_operation_dict['Site3'])):
        site3_rechtangular_through_step_face_id = rechtangular_through_step_bottom_face_line_original[rechtangular_through_step_operation_dict['Site3'][i][3]]
        site3_rechtangular_through_step_face = 'Face{:d}'.format(site3_rechtangular_through_step_face_id[0])
        adaptive_operation(site3_rechtangular_through_step_face,0,auswahl_werkzeug,0,name=i+80)
if 17.0 in dict_all:
    for i in range (0,len(slanted_through_step_operation_dict['Site3'])):
        site3_slanted_through_step_face_id = slanted_through_step_bottom_face_line_original[slanted_through_step_operation_dict['Site3'][i][3]]
        site3_slanted_through_step_face = 'Face{:d}'.format(site3_slanted_through_step_face_id[0])
        adaptive_operation(site3_slanted_through_step_face,0,auswahl_werkzeug,0,name=i+90)
if 20.0 in dict_all:
    for i in range (0,len(vertical_circular_end_blind_slot_operation_dict['Site3'])):
        site3_vertical_circular_end_blind_slot_face_id = vertical_circular_end_blind_slot_bottom_face_line_original[vertical_circular_end_blind_slot_operation_dict['Site3'][i][3]]
        site3_vertical_circular_end_blind_slot_face = 'Face{:d}'.format(site3_vertical_circular_end_blind_slot_face_id[0])
        adaptive_operation(site3_vertical_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+100)
if 21.0 in dict_all:
    for i in range (0,len(horizontal_circular_end_blind_slot_operation_dict['Site3'])):
        site3_horizontal_circular_end_blind_slot_face_id = horizontal_circular_end_blind_slot_bottom_face_line_original[horizontal_circular_end_blind_slot_operation_dict['Site3'][i][3]]
        site3_horizontal_circular_end_blind_slot_face = 'Face{:d}'.format(site3_horizontal_circular_end_blind_slot_face_id[0])
        adaptive_operation(site3_horizontal_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+110)
if 23.0 in dict_all:
    for i in range (0,len(six_sides_pocket_operation_dict['Site3'])):
        site3_six_sides_pocket_face_id = six_sides_pocket_bottom_face_line_original[six_sides_pocket_operation_dict['Site3'][i][3]]
        site3_six_sides_pocket_face = 'Face{:d}'.format(site3_six_sides_pocket_face_id[0])
        adaptive_operation(site3_six_sides_pocket_face,0,auswahl_werkzeug,0,name=i+120)

job.PostProcessorOutputFile = gcodePath_site3
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
gcode = post.export(postlist, gcodePath_site3, job.PostProcessorArgs)
DOC.recompute()
print("--- done ---")
App.closeDocument(file_name_1)

# Schritt5: site4 Bearbeitung
DOC = App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
Part1 =  DOC.getObject(file_name_2)

obj = App.ActiveDocument.Solid
rot = App.Rotation(App.Vector(1,0,0),-90)
centre = App.Vector(centervector)
pos = obj.Placement.Base
newplace = App.Placement(pos,rot,centre)
obj.Placement = newplace

Gui.activateWorkbench("PathWorkbench")
job = PathJob.Create('Job_site4', [Part1], None)
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

#Werkzeug Aufladen
tool1_diameter = werkzeug(toolpath1, 'tool1')
tool2_diameter = werkzeug(toolpath2, 'tool2')
App.getDocument(file_name_1).getObject('ToolBit001').ShapeName = "endmill"
DOC.recompute()
werkzeuglist = ['tool1','tool2']
auswahl_werkzeug = werkzeuglist[0]
#operation
if 10.0 in dict_all:
    for i in range (0,len(pocket_operation_dict['Site4'])):
        site4_pocket_face_id = bottom_face_line_original[pocket_operation_dict['Site4'][i][3]]
        site4_pocket_face = 'Face{:d}'.format(site4_pocket_face_id[0])
        adaptive_operation(site4_pocket_face,0,auswahl_werkzeug,0,name=i)
if 2.0 in dict_all:
    for i in range (0,len(blind_hole_operation_dict['Site4'])):
        site4_blind_hole_face_id = blind_hole_bottom_face_line_original[blind_hole_operation_dict['Site4'][i][3]]
        site4_blind_hole_face = 'Face{:d}'.format(site4_blind_hole_face_id[0])
        adaptive_operation(site4_blind_hole_face, 0, auswahl_werkzeug, 0, name=i+10)
if 14.0 in dict_all:
    for i in range (0,len(blind_step_operation_dict['Site4'])):
        site4_blind_step_face_id = blind_step_bottom_face_line_original[blind_step_operation_dict['Site4'][i][3]]
        site4_blind_step_face = 'Face{:d}'.format(site4_blind_step_face_id[0])
        adaptive_operation(site4_blind_step_face, 0, auswahl_werkzeug, 0, name=i + 20)
if 7.0 in dict_all:
    for i in range (0,len(rechtgular_through_slot_operation_dict['Site4'])):
        site4_rechtgular_through_slot_face_id = rechtgular_through_slot_bottom_face_line_original[rechtgular_through_slot_operation_dict['Site4'][i][3]]
        site4_rechtgular_through_slot_face = 'Face{:d}'.format(site4_rechtgular_through_slot_face_id[0])
        adaptive_operation(site4_rechtgular_through_slot_face,0,auswahl_werkzeug,0,name=i+30)
if 8.0 in dict_all:
    for i in range (0,len(rechtgular_blind_slot_operation_dict['Site4'])):
        site4_rechtgular_blind_slot_face_id = rechtgular_blind_slot_bottom_face_line_original[rechtgular_blind_slot_operation_dict['Site4'][i][3]]
        site4_rechtgular_blind_slot_face = 'Face{:d}'.format(site4_rechtgular_blind_slot_face_id[0])
        adaptive_operation(site4_rechtgular_blind_slot_face,0,auswahl_werkzeug,0,name=i+40)
if 9.0 in dict_all:
    for i in range (0,len(triangular_pocket_operation_dict['Site4'])):
        site4_triangular_pocket_face_id = triangular_pocket_bottom_face_line_original[triangular_pocket_operation_dict['Site4'][i][3]]
        site4_triangular_pocket_face = 'Face{:d}'.format(site4_triangular_pocket_face_id[0])
        adaptive_operation(site4_triangular_pocket_face,0,auswahl_werkzeug,0,name=i+50)
if 12.0 in dict_all:
    for i in range (0,len(triangular_blind_step_operation_dict['Site4'])):
        site4_triangular_blind_step_face_id = triangular_blind_step_bottom_face_line_original[triangular_blind_step_operation_dict['Site4'][i][3]]
        site4_triangular_blind_step_face = 'Face{:d}'.format(site4_triangular_blind_step_face_id[0])
        adaptive_operation(site4_triangular_blind_step_face,0,auswahl_werkzeug,0,name=i+60)
if 13.0 in dict_all:
    for i in range (0,len(circular_blind_step_operation_dict['Site4'])):
        site4_circular_blind_step_face_id = circular_blind_step_bottom_face_line_original[circular_blind_step_operation_dict['Site4'][i][3]]
        site4_circular_blind_step_face = 'Face{:d}'.format(site4_circular_blind_step_face_id[0])
        adaptive_operation(site4_circular_blind_step_face,0,auswahl_werkzeug,0,name=i+70)
if 15.0 in dict_all:
    for i in range (0,len(rechtangular_through_step_operation_dict['Site4'])):
        site4_rechtangular_through_step_face_id = rechtangular_through_step_bottom_face_line_original[rechtangular_through_step_operation_dict['Site4'][i][3]]
        site4_rechtangular_through_step_face = 'Face{:d}'.format(site4_rechtangular_through_step_face_id[0])
        adaptive_operation(site4_rechtangular_through_step_face,0,auswahl_werkzeug,0,name=i+80)
if 17.0 in dict_all:
    for i in range (0,len(slanted_through_step_operation_dict['Site4'])):
        site4_slanted_through_step_face_id = slanted_through_step_bottom_face_line_original[slanted_through_step_operation_dict['Site4'][i][3]]
        site4_slanted_through_step_face = 'Face{:d}'.format(site4_slanted_through_step_face_id[0])
        adaptive_operation(site4_slanted_through_step_face,0,auswahl_werkzeug,0,name=i+90)
if 20.0 in dict_all:
    for i in range (0,len(vertical_circular_end_blind_slot_operation_dict['Site4'])):
        site4_vertical_circular_end_blind_slot_face_id = vertical_circular_end_blind_slot_bottom_face_line_original[vertical_circular_end_blind_slot_operation_dict['Site4'][i][3]]
        site4_vertical_circular_end_blind_slot_face = 'Face{:d}'.format(site4vertical_circular_end_blind_slot_face_id[0])
        adaptive_operation(site4_vertical_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+100)
if 21.0 in dict_all:
    for i in range (0,len(horizontal_circular_end_blind_slot_operation_dict['Site4'])):
        site4_horizontal_circular_end_blind_slot_face_id = horizontal_circular_end_blind_slot_bottom_face_line_original[horizontal_circular_end_blind_slot_operation_dict['Site4'][i][3]]
        site4_horizontal_circular_end_blind_slot_face = 'Face{:d}'.format(site4_horizontal_circular_end_blind_slot_face_id[0])
        adaptive_operation(site4_horizontal_circular_end_blind_slot_face,0,auswahl_werkzeug,0,name=i+110)
if 23.0 in dict_all:
    for i in range (0,len(six_sides_pocket_operation_dict['Site4'])):
        site4_six_sides_pocket_face_id = six_sides_pocket_bottom_face_line_original[six_sides_pocket_operation_dict['Site4'][i][3]]
        site4_six_sides_pocket_face = 'Face{:d}'.format(site4_six_sides_pocket_face_id[0])
        adaptive_operation(site4_six_sides_pocket_face,0,auswahl_werkzeug,0,name=i+120)

job.PostProcessorOutputFile = gcodePath_site4
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
gcode = post.export(postlist, gcodePath_site4, job.PostProcessorArgs)
DOC.recompute()

Gui.doCommand('exit()') # Wenn das Programm endet, beende die Anwendung.















