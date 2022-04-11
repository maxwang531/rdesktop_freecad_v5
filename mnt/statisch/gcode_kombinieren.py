# import sys
import os
# Eingabe- und Ausgabepfade von Bearbeitungscodes
file_top = '/config/ausgabe_ngc/txt/top_operation.txt'
file_site1 = '/config/ausgabe_ngc/txt/site1_operation.txt'
file_site2 = '/config/ausgabe_ngc/txt/site2_operation.txt'
file_site3 = '/config/ausgabe_ngc/txt/site3_operation.txt'
file_site4 = '/config/ausgabe_ngc/txt/site4_operation.txt'
file_top_neu = '/config/ausgabe_ngc/neu_txt/top_operation.txt'
file_site1_neu = '/config/ausgabe_ngc/neu_txt/site1_operation.txt'
file_site2_neu = '/config/ausgabe_ngc/neu_txt/site2_operation.txt'
file_site3_neu = '/config/ausgabe_ngc/neu_txt/site3_operation.txt'
file_site4_neu = '/config/ausgabe_ngc/neu_txt/site4_operation.txt'

'''Wenn es Verarbeitungsinformationen gibt, den Anfang und das Ende entfernen, wenn es keine Verarbeitungsinformationen gibt, alles löschen.'''
data_top = []
for line in open(file_top,"r"):
    data_top.append(line)
if len(data_top) != 10:
    del data_top[0:13]
    data_top.insert(0, 'G0 A90\n')
    del data_top[len(data_top) - 3:len(data_top)]
    f=open('/config/ausgabe_ngc/neu_txt/top_operation_neu.txt',"w")
    for line in data_top:
        f.write(line+'\n')
    f.close()
if len(data_top) == 10:
    del data_top[0:10]
    f=open('/config/ausgabe_ngc/neu_txt/top_operation_neu.txt',"w")
    for line in data_top:
        f.write(line+'\n')
    f.close()

data_site1 = []
for line in open('/config/ausgabe_ngc/txt/site1_operation.txt',"r"):
    data_site1.append(line)
if len(data_site1) != 10:
    del data_site1[0:13]
    del data_site1[len(data_site1) - 3:len(data_site1)]
    data_site1.insert(0, 'G0 A0\n')
    data_site1.insert(1, 'G0 B180\n')
    f=open('/config/ausgabe_ngc/neu_txt/site1_operation_neu.txt',"w")
    for line in data_site1:
        f.write(line+'\n')
    f.close()
if len(data_site1) == 10:
    del data_site1[0:10]
    f=open('/config/ausgabe_ngc/neu_txt/site1_operation_neu.txt',"w")
    for line in data_site1:
        f.write(line+'\n')
    f.close()

data_site2 = []
for line in open('/config/ausgabe_ngc/txt/site2_operation.txt',"r"):
    data_site2.append(line)
if len(data_site2) != 10:
    del data_site2[len(data_site2) - 3:len(data_site2)]
    del data_site2[0:13]
    data_site2.insert(0, 'G0 A0\n')
    data_site2.insert(1, 'G0 B270\n')
    f=open('/config/ausgabe_ngc/neu_txt/site2_operation_neu.txt',"w")
    for line in data_site2:
        f.write(line+'\n')
    f.close()
if len(data_site2) == 10:
    del data_site2[0:10]
    f=open('/config/ausgabe_ngc/neu_txt/site2_operation_neu.txt',"w")
    for line in data_site2:
        f.write(line+'\n')
    f.close()

data_site3 = []
for line in open('/config/ausgabe_ngc/txt/site3_operation.txt',"r"):
    data_site3.append(line)
if len(data_site3) != 10:
    del data_site3[len(data_site3) - 3:len(data_site3)]
    del data_site3[0:13]
    data_site3.insert(0, 'G0 A0\n')
    data_site3.insert(1, 'G0 B0\n')
    f=open('/config/ausgabe_ngc/neu_txt/site3_operation_neu.txt',"w")
    for line in data_site3:
        f.write(line+'\n')
    f.close()
if len(data_site3) == 10:
    del data_site3[0:10]
    f=open('/config/ausgabe_ngc/neu_txt/site3_operation_neu.txt',"w")
    for line in data_site3:
        f.write(line+'\n')
    f.close()

data_site4 = []
for line in open('/config/ausgabe_ngc/txt/site4_operation.txt',"r"):
    data_site4.append(line)
if len(data_site4) != 10:
    del data_site4[len(data_site4) - 3:len(data_site4)]
    del data_site4[0:13]
    data_site4.insert(0, 'G0 A0\n')
    data_site4.insert(1, 'G0 B90\n')
    f=open('/config/ausgabe_ngc/neu_txt/site4_operation_neu.txt',"w")
    for line in data_site4:
        f.write(line+'\n')
    f.close()
if len(data_site4) == 10:
    del data_site4[0:10]
    f=open('/config/ausgabe_ngc/neu_txt/site4_operation_neu.txt',"w")
    for line in data_site4:
        f.write(line+'\n')
    f.close()

'''Die Bearbeitungsinformationen aller 5 Flächen zusammenführen.'''
data=data_top+data_site1+data_site2+data_site3+data_site4
data.insert(0,'G17 G54 G40 G49 G80 G90\n')
data.insert(1,'G21\n')
data.insert(2,'M5\n')
data.insert(3,'M6 T1 \n')
data.insert(4,'G43 H1  \n')
data.insert(5,'M3 S10000 \n')
data.insert(6,'F2000 \n')
data.insert(len(data)+1,'M05\n')
data.insert(len(data)+2,'G17 G54 G90 G80 G40\n')
data.insert(len(data)+2,'M2\n')
f=open('/config/ausgabe_ngc/neu_txt/operation_neu.txt',"w")
for line in data:
    f.write(line+'\n')
f.close()
'''ngc-Datei ausgeben'''
f=open('/config/ausgabe_ngc/statisch_operation.ngc',"w")
for line in data:
    f.write(line+'\n')
f.close()
Gui.doCommand('exit()')

