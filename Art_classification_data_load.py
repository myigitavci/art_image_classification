# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:37:50 2022

@author: yigitavcii
"""
import glob
import os
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

import pandas as pd
import scipy.io
from sklearn.metrics import accuracy_score
#Import svm model
from sklearn import svm
import matplotlib.pyplot as plt

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import LeaveOneOut
import pandas as pd
import xml.etree.ElementTree as ET
import io
from bs4 import BeautifulSoup 
import glob
import shutil
import os
#%%
dpRoot = 'D:/ee58j_final_project'
os.chdir(dpRoot)

dpMetaData=dpRoot+'/xml2'
dpJpgs=dpRoot+'/jpg2'
data = sorted(glob.glob(os.path.join(dpMetaData, '0*')))
jpg_data = sorted(glob.glob(os.path.join(dpJpgs, '0*')))

#pd.read_xml('D:/ee58j_final_project/xml2/0000001_SK-A-4878.xml')

with open('D:/ee58j_final_project/xml2/0000001_SK-A-4878.xml', 'r') as f:
        xmldata = f.read() 

# Passing the stored data inside the beautifulsoup parser 
bs_data = BeautifulSoup(xmldata, 'xml') 
# Finding all instances of tag   
b_unique = bs_data.find_all('creator') 


#%%
dict_of_creators={}
d=0
for i in range(0,len(data)):
    
 try:
# Reading the data inside the xml file to a variable under the name  data
    with open(data[i], 'r') as f:
        xmldata = f.read() 

# Passing the stored data inside the beautifulsoup parser 
    bs_data = BeautifulSoup(xmldata, 'xml') 
# Finding all instances of tag   
    b_unique = bs_data.find_all('creator') 
    a=b_unique.pop()
    c=a.text.split(':')
    creator=c[1]
    #print(creator) 
    if creator in dict_of_creators:
        count=dict_of_creators.get(creator)
        count=count+1
        dict_of_creators[creator]=count
    else:
        dict_of_creators[creator] = 1

        
        
 except:
  i=i+1   
  d=d+1    
  print(d)
  print(data[i])
  #%%
d=0
from operator import itemgetter
sorted_dict=sorted(dict_of_creators.items(), key=itemgetter(1),reverse=True)
#%%
for i in range(0,53):
    path=dpRoot+'/art_imgs_50/'+sorted_dict[i][0]
    isExist = os.path.exists(path)

    if not isExist:
  
  # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")
        
#%%
for i in range(0,len(data)):
 
    jpg_file=jpg_data[i]    
    try:
# Reading the data inside the xml file to a variable under the name  data
     with open(data[i], 'r') as f:
        xmldata = f.read() 

# Passing the stored data inside the beautifulsoup parser 
     bs_data = BeautifulSoup(xmldata, 'xml') 
# Finding all instances of tag   
     b_unique = bs_data.find_all('creator') 
     a=b_unique.pop()
     c=a.text.split(':')
     creator=c[1]   
     for j in range(0,53): 
        creator_2=sorted_dict[j][0]
    #print(creator) 
        if creator == creator_2 and creator !=' ':
            try:
               # print('writing')
                dst_dir = dpRoot+'/art_imgs_50/'+creator+'/'+str(i)+'.jpg'
                shutil.copy(jpg_file, dst_dir)
            except:
                dst_dir=dpRoot+'/art_imgs_50/'+creator+str(i)+'.jpg'
                shutil.copy(jpg_file, dst_dir)
    except:
        i=i+1
        
#%%

# test split
dpRoot = 'D:/ee58j_final_project'
os.chdir(dpRoot)
dpImgs=dpRoot+'/art_imgs_50'
dpTest=dpRoot+'/test_set_50'
data = sorted(glob.glob(os.path.join(dpImgs, ' *')))

for i in range(0,len(data)):
    ind= data[i].find(' ')
    path=dpImgs+'/'+data[i][ind:]
    creator_data = sorted(glob.glob(os.path.join(path, '*')))
    for j in range(0,int(15*len(creator_data)/100)):
        source=creator_data[j]
        dst_dir = dpRoot+'/test_set_50/'+data[i][ind:]+'/'+str(j)+'.jpg'
        shutil.move(source, dst_dir)        