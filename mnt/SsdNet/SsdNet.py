import os
import pandas as pd
import numpy as np
import csv
import utils.binvox_rw
from utils.augmentations import SSDAugmentation
from data import *
import torch
import torch.backends.cudnn as cudnn
from utils.ssd import build_ssd
from torch.autograd import Variable
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import pow
import matplotlib.patches as mpatches


if torch.cuda.is_available():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')

def load_pretrained_model():
    ssd_net = build_ssd(cfg['min_dim'], cfg['num_classes'])
    net = ssd_net

    net = torch.nn.DataParallel(ssd_net)
    cudnn.benchmark = True

    ssd_net.load_weights('weights/VOC.pth')

    return net.cuda()


def tensor_to_float(val):
    
    if val < 0:
        val = 0
    
    if val > 1:
        val = 1
    
    return float(val)

def rotate_sample(sample,rotation, reverse = False):

    if reverse:
        if rotation == 1:
            sample = np.rot90(sample, -2, (0,1)).copy()  
        elif rotation == 2:
            sample = np.rot90(sample, -1, (0,1)).copy()  
        elif rotation == 3:
            sample = np.rot90(sample, -1, (1,0)).copy()  
        elif rotation == 4:
            sample = np.rot90(sample, -1, (2,0)).copy()  
        elif rotation == 5:
            sample = np.rot90(sample, -1, (0,2)).copy() 
    else:
        if rotation == 1:
            sample = np.rot90(sample, 2, (0,1)).copy()  
        elif rotation == 2:
            sample = np.rot90(sample, 1, (0,1)).copy()  
        elif rotation == 3:
            sample = np.rot90(sample, 1, (1,0)).copy()  
        elif rotation == 4:
            sample = np.rot90(sample, 1, (2,0)).copy()  
        elif rotation == 5:
            sample = np.rot90(sample, 1, (0,2)).copy() 
        
    return sample

def soft_nms_pytorch(boxes, box_scores, sigma=0.5):

    dets = boxes[:,0:6].copy()*1000
    
    N = dets.shape[0]
    
    indexes = torch.arange(0, N, dtype=torch.double).view(N, 1).cpu()
    dets = torch.from_numpy(dets).double().cpu()
    scores = torch.from_numpy(box_scores.copy()).double().cpu()
        
    dets = torch.cat((dets, indexes), dim=1).cpu()
    

    z1 = dets[:, 0]
    y1 = dets[:, 1]
    x1 = dets[:, 2]
    z2 = dets[:, 3]
    y2 = dets[:, 4]
    x2 = dets[:, 5]
    #scores = box_scores
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)* (z2 - z1 + 1)

    for i in range(N):
        tscore = scores[i].clone()
        pos = i + 1

        if i != N - 1:
            maxscore, maxpos = torch.max(scores[pos:], dim=0)
            if tscore < maxscore:
                dets[i], dets[maxpos.item() + i + 1] = dets[maxpos.item() + i + 1].clone(), dets[i].clone()
                scores[i], scores[maxpos.item() + i + 1] = scores[maxpos.item() + i + 1].clone(), scores[i].clone()
                areas[i], areas[maxpos + i + 1] = areas[maxpos + i + 1].clone(), areas[i].clone()


        # IoU calculate
        zz1 = np.maximum(dets[i, 0].to("cpu").numpy(), dets[pos:, 0].to("cpu").numpy())
        yy1 = np.maximum(dets[i, 1].to("cpu").numpy(), dets[pos:, 1].to("cpu").numpy())
        xx1 = np.maximum(dets[i, 2].to("cpu").numpy(), dets[pos:, 2].to("cpu").numpy())
        zz2 = np.minimum(dets[i, 3].to("cpu").numpy(), dets[pos:, 3].to("cpu").numpy())
        yy2 = np.minimum(dets[i, 4].to("cpu").numpy(), dets[pos:, 4].to("cpu").numpy())
        xx2 = np.minimum(dets[i, 5].to("cpu").numpy(), dets[pos:, 5].to("cpu").numpy())
        
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        l = np.maximum(0.0, zz2 - zz1 + 1)
        inter = torch.tensor(w * h * l).cpu()
        ovr = torch.div(inter, (areas[i] + areas[pos:] - inter)).cpu()

        # Gaussian decay
        weight = torch.exp(-(ovr * ovr) / sigma).cpu()
        
        
        
        scores[pos:] = weight * scores[pos:]


    #print(scores)
    max_margin = 0
    thresh = 0
    for i in range(scores.shape[0]-1):
        if scores[i] - scores[i + 1] > max_margin:
            max_margin = scores[i] - scores[i + 1]
            thresh = (scores[i] + scores[i+1])/2
    #thresh = (scores[1] + scores[2])/2
       
    
    
    keep = dets[:, 6][scores > thresh].int()
    #print(keep.shape)
    
    

    return keep.to("cpu").numpy()

def get_predicted_label(filename, net, csvfilename):
    with open(filename+'.binvox', 'rb') as f:
        model = utils.binvox_rw.read_as_3d_array(f).data
    
    transform=SSDAugmentation(cfg['min_dim'],MEANS,phase='test') #数据增强
    
    images = []
    
    for rot in range(6):
        img, _ = create_img(model, rot)
                
        img, _, _ = transform(img, 0, 0)
        
        images.append(img)
        
    images = torch.tensor(images).permute(0, 3, 1, 2).float()
    
    
    images = Variable(images.cuda())
    #images = images.cuda()
                    
    out = net(images, 'test') #加了apply
    out.cuda()#数据转译至GPU
    
    cur_boxes = np.zeros((0,8)) #建个0x8的元组，是个矩阵
    #print (cur_boxes)
    
    
    for i in range(6):

        
        for j in range(out.shape[1]):
            label = out[i,j,1].detach().cpu()
            #print('label:',label)
            #print(out[i,j,1])
            
                    
            if label == 0:
                continue
            
            
            
                    
            score = out[i,j,0].detach().cpu()
                    
            x1 = tensor_to_float(out[i,j,2])
            y1 = tensor_to_float(out[i,j,3])
            x2 = tensor_to_float(out[i,j,4])
            y2 = tensor_to_float(out[i,j,5])
            z1 = 0.0
            z2 = tensor_to_float(out[i,j,6])
            #print('x1:',x1*40,'y1:',y1)

            
            if x1 >= x2 or y1 >= y2 or z2 <= 0:
                continue
            
          
            a = z1
            b = y1
            c = x1
            d = z2
            e = y2
            f = x2
        
            if i == 1:
                a = 1-z2
                b = 1-y2
                c = x1
                d = 1-z1
                e = 1-y1
                f = x2
            elif i == 2:
                a = y1
                b = 1-z2
                c = x1
                d = y2
                e = 1-z1
                f = x2
            elif i == 3:
                a = 1-y2
                b = z1
                c = x1
                d = 1-y1
                e = z2
                f = x2
            elif i == 4:
                a = 1-x2
                b = y1
                c = z1
                d = 1-x1
                e = y2
                f = z2
            elif i == 5:
                a = x1
                b = y1
                c = 1-z2
                d = x2
                e = y2
                f = 1-z1
            
            cur_boxes = np.append(cur_boxes,np.array([a,b,c,d,e,f,label-1,score]).reshape(1,8),axis=0) #axis指定轴


    keepidx = soft_nms_pytorch(cur_boxes[:,:7], cur_boxes[:,-1])
    #print(keepidx)
    cur_boxes = cur_boxes[keepidx,:]
    #print(cur_boxes)
    
    
    cur_boxes[:,0:6] = modellange*cur_boxes[:,0:6] # Der Parameter entspricht der Seitenlänge des Würfels
    #print(cur_boxes) # x_min, y_min, z_min, x_max, y_max, z_max
    list= cur_boxes
    name=['x-','y-','z-','x+','y+','z+','type','Pozent']
    test = pd.DataFrame(columns=name, data=list)
    test.to_csv(csvfilename) # Als csv-Datei speichern.
    return cur_boxes

def get_lvec(labels):
    results = np.zeros(24)
    
    
    for i in labels:
        results[int(i)] += 1
    
    return results.astype(int)


    
def eval_metric(pre,trul,tp):
    precision = tp/pre
    
    recall = tp/trul
    
    return precision, recall


net = load_pretrained_model()
filename = '/docker_demo/src/eingabe_model/bool_model/Common' # binvox-Datei
csvfilename = '/docker_demo/src/eingabe_model/csv_file/ssd_information.csv' # gespeicherte Datendatei

modellangefile = '/config/eingabe_model/csv_file/modellange.csv'
corpusData = pd.read_csv(modellangefile)
modellange = corpusData.iloc[0,1] # Die Daten der Kantenlänge des Modells lesen.

labels = get_predicted_label(filename,net,csvfilename)











