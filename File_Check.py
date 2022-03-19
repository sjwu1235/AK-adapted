import json
from pathlib import Path
import time
import pandas as pd
import os.path
import shutil
import os

'''
# uncomment this block and comment out block below to get masters and pivots from using inputs.json files
with open(r'Scihub_inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

directory = input_deets['directory']    
master = pd.read_excel(input_deets['master'])
pivots = pd.read_excel(input_deets['pivots'])
'''
directory = "C:\\Users\\sjwu1\\Journal_Data\\Scihub"
masters = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\Master lists\\AER_master.xlsx")
pivots = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\pivots\\AER_pivots.xlsx")

#src_folder = r"C:\Users\sjwu1\Journal_Data"
#dst_folder = r"C:\Users\sjwu1\Master_\AER_data"

total=0
fulllist_s_1940=0
for ind in pivots.index:
    temp3=masters[masters['issue_url']==pivots['issue_url'][ind]]
    downloaded=0
    for ind2 in temp3.index:
        pdf_file_name=masters['stable_url'][ind2].split('/')[-1]+".pdf"
        if (pivots['year'][ind]>=1940):
            fulllist_s_1940+=1
        #print(pdf_file_name+" "+str(os.path.isfile(directory+pdf_file_name)))
        if(os.path.isfile(directory+"\\"+pdf_file_name)):
            downloaded+=1
            #source = directory + "\\"+ pdf_file_name
            #destination = dst_folder +"\\"+ pdf_file_name
            #shutil.move(source,destination)
    total=total+downloaded
    print(str(pivots['year'][ind])+" "+str(pivots['no_docs'][ind])+" "+str(pivots['issue_url'][ind])+" "+str(downloaded))

print(total)
print(fulllist_s_1940)
