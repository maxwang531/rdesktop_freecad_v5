'''Dieses Programm verarbeitet die Ausgabedaten von SsdNet und vervollständigt schließlich die Lokalisierung der Unterseite des Merkmals.'''

#import sys
import sys
import os
#FreeCAD import
from FreeCAD import Base, Rotation, Vector
from math import pi, sin, cos
import csv
import numpy as np
import pandas as pd
from pandas import DataFrame,Series
from scipy.spatial import KDTree
import FreeCAD as App
import FreeCADGui as Gui

# Lösche das Voxelmodell, um Fehler in der nächsten Runde von Operationen zu vermeiden.
os.system("sh /config/eingabe_model/bool_model/model_ssdnet_delete.sh")

# csv-Dateipfad in der Modelldatenverarbeitung.
filename = '/config/eingabe_model/bool_model/Common.FCStd' #Model nach der boolschen Operation
filepath_original = '/config/eingabe_model/model.FCStd' #Model von der boolschen Operation
csvfilename = '/config/eingabe_model/csv_file/model_information.csv'
SsdNetfile = '/config/eingabe_model/csv_file/ssd_information.csv'
freeCADfile = '/config/eingabe_model/csv_file/model_information.csv'
resultfile = '/config/eingabe_model/csv_file/result_information.csv'

'''Modeldatenbearbeitung'''
# Schritt1: Das Modell nach der booleschen Operation einlesen und den Schwerpunkt jeder Fläche des Modells berechnen.
DOC=FreeCAD.openDocument(filename)
DOC.recompute()
DOC = FreeCAD.activeDocument()
DOC.recompute()
obj = App.ActiveDocument.getObject('Common')
template  ='Face {}: CenterOfMass --> ({:.1f}, {:.1f}, {:.1f})'
list=[]
for i, face in enumerate(obj.Shape.Faces, start=1):
    centerofmass = face.CenterOfMass
    list.append([i, '%.1f' % centerofmass.x , '%.1f' % centerofmass.y , '%.1f' % centerofmass.z])
    test2 = pd.DataFrame( data=list, columns=['Face','X','Y','Z'])
    test2.to_csv(csvfilename) # Ergebnis in csv-Datei speichern.

# Schritt2: Das Modell vor der booleschen Operation einlesen und den minimalen XYZ-Koordinatenwert des Modells berechnen.
DOC=App.openDocument(filepath_original)
DOC.recompute()
DOC = App.activeDocument()
DOC.recompute()
obj = App.ActiveDocument.getObject('Solid')
x_min = obj.Shape.BoundBox.XMin
y_min = obj.Shape.BoundBox.YMin
z_min = obj.Shape.BoundBox.ZMin


'''SsdNet Datenbearbeitung'''
# Schritt1: SsdNet Daten einlesen (csv-Datei).
corpusData = pd.read_csv(SsdNetfile) #Information in corpusData speichern.
x=corpusData.shape[1] # Anzahl der Spalten
y=corpusData.shape[0] # Anzahl der Zeilen

# Schritt2: Daten ausgeben in list
Type = corpusData.iloc[0:y,7].values.tolist()
xmin = corpusData.iloc[0:y,1].values.tolist()
xmin = [i +x_min for i in xmin]
xmax = corpusData.iloc[0:y,4].values.tolist()
xmax = [i +x_min for i in xmax]
ymin = corpusData.iloc[0:y,2].values.tolist()
ymin = [i +y_min for i in ymin]
ymax = corpusData.iloc[0:y,5].values.tolist()
ymax = [i +y_min for i in ymax]
zmin = corpusData.iloc[0:y,3].values.tolist()
zmin = [i +z_min for i in zmin]
zmax = corpusData.iloc[0:y,6].values.tolist()
zmax = [i +z_min for i in zmax]

# Schritt3: Daten Bearbeitung (Liste in Array umwandeln)
xminnp = np.array(xmin)
xmaxnp = np.array(xmax)
yminnp = np.array(ymin)
ymaxnp = np.array(ymax)
zminnp = np.array(zmin)
zmaxnp = np.array(zmax)

# Schritt4: Die Koordinaten des Schwerpunkts jeder Fläche des Begrenzungsrahmens des Merkmals.
# bottom
bottomX = (xminnp+xmaxnp)/2
bottomX = bottomX.tolist()
bottomY = (yminnp+ymaxnp)/2
bottomY = bottomY.tolist()
bottomZ = zmin
#top
topX = bottomX
topY = bottomY
topZ = zmax
#site1
site1X = xmin
site1Y = bottomY
site1Z = (zminnp+zmaxnp)/2
site1Z = site1Z.tolist()
#site2
site2X = bottomX
site2Y = ymax
site2Z = site1Z
#site3
site3X = xmax
site3Y = bottomY
site3Z = site1Z
#site4
site4X = bottomX
site4Y = ymin
site4Z = site1Z

# Schritt5: DataFrame von SsdNet (Typ und Schwerpunkt von jeder Fläche)
data = {'Type':Series(Type),'bottomX':Series(bottomX),'bottomY':Series(bottomY),'bottomZ':Series(bottomZ),'topX':Series(topX),'topY':Series(topY),'topZ':Series(topZ),'site1X':Series(site1X),'site1Y':Series(site1Y),'site1Z':Series(site1Z),'site2X':Series(site2X),'site2Y':Series(site2Y),'site2Z':Series(site2Z),'site3X':Series(site3X),'site3Y':Series(site3Y),'site3Z':Series(site3Z),'site4X':Series(site4X),'site4Y':Series(site4Y),'site4Z':Series(site4Z)}
df = DataFrame(data) #DataFrame erstellen

'''Interagiere mit den von FreeCAD gelesenen Modellinformationen, um Flächen zu paaren.'''
# Schritt1: csv-Datei einlesen.
corpusData2 = pd.read_csv(freeCADfile)
s = corpusData2.shape[0]
# Schritt2: Daten Bearebeitung (DataFrame von FreeCAD: Fläche und Schwerpunktkoordinaten)
Face= corpusData2.iloc[0:s,1].values.tolist()
koorX = corpusData2.iloc[0:s,2].values.tolist()
koorY = corpusData2.iloc[0:s,3].values.tolist()
koorZ = corpusData2.iloc[0:s,4].values.tolist()
data2 = {'Face':Series(Face), 'koorX':Series(koorX), 'koorY':Series(koorY), 'koorZ':Series(koorZ)}
df2 = DataFrame(data2)

''' Die Verbindung der Flächen wird durch die Suche nach den nächstgelegenen Schwerpunktkoordinaten hergestellt.'''
NDIM = 3
# Schritt1: DataFrame von FreeCAD Bearbeitung
p = df2.shape[0]
df2point = df2.iloc[0:p,1:4].values.tolist()
df2pointnp = np.array(df2point)

# Schritt2: Wähle die Punkte auf der Vorhersagefläche aus, die abgeglichen werden müssen
q = df.shape[0]
bottompoint = df.iloc[0:q,1:4].values.tolist() #只匹配了bottomXYZ
toppoint = df.iloc[0:q,4:7].values.tolist()
site1point = df.iloc[0:q,7:10].values.tolist()
site2point = df.iloc[0:q,10:13].values.tolist()
site3point = df.iloc[0:q,13:16].values.tolist()
site4point = df.iloc[0:q,16:19].values.tolist()

# Schritt3: Finde den nächstgelegenen Punkt mit KDTree
tree = KDTree(df2pointnp, leafsize=df2pointnp.shape[0]+1)
distances, ndxbottom = tree.query([bottompoint], k=1) # k ist der Anzahl des Punkts
distances, ndxtop = tree.query([toppoint], k=1)
distances, ndxsite1 = tree.query([site1point], k=1)
distances, ndxsite2 = tree.query([site2point], k=1)
distances, ndxsite3 = tree.query([site3point], k=1)
distances, ndxsite4 = tree.query([site4point], k=1)
bottom = (ndxbottom[0]+1).tolist()
top = (ndxtop[0]+1).tolist()
site1 = (ndxsite1[0]+1).tolist()
site2 = (ndxsite2[0]+1).tolist()
site3 = (ndxsite3[0]+1).tolist()
site4 = (ndxsite4[0]+1).tolist()
# Schritt4: Ergebnis ausgeben (csv-Dartei).
data3 = {'Type':Series(Type),'Bottom':Series(bottom),'Top':Series(top),'Site1':Series(site1),'Site2':Series(site2),'Site3':Series(site3),'Site4':Series(site4)}
result = DataFrame(data3)
result.to_csv(resultfile)

# Wenn das Programm endet, beende die Anwendung.
Gui.doCommand('exit()')
