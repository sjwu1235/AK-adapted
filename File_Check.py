import json
from pathlib import Path
import time
import pandas as pd
import os.path

with open(r'inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

directory = input_deets['directory']
datadump_loc = input_deets['datadump']
datadump=pd.read_excel(datadump_loc)
start_loc = input_deets['pivots']
start_year=input_deets['start_year']
end_year=input_deets['end_year']
sleep_time=input_deets['sleep_time']

temp = pd.read_excel(directory+"\\Master lists\\"+input_deets['journal_name']+"_master.xlsx")
temp2 = pd.read_excel(directory+"\\pivots\\AER2_pivots.xlsx")
'''
downloaded=0
for ind in temp.index:
    pdf_file_name=temp['stable_url'][ind][29:]+".pdf"
    #print(pdf_file_name+" "+str(os.path.isfile(directory+pdf_file_name)))
    if(os.path.isfile(directory+"\\"+pdf_file_name)):
        downloaded+=1
print(downloaded)
print(temp.shape)

'''

import shutil
import os
src_folder = r"C:\Users\sjwu1\Journal_Data"
dst_folder = r"C:\Users\sjwu1\Master_\AER_data"

total=0
for ind in temp2.index:
    temp3=temp[temp['issue_url']==temp2['issue_url'][ind]]
    downloaded=0
    for ind2 in temp3.index:
        pdf_file_name=temp['stable_url'][ind2][29:]+".pdf"
        #print(pdf_file_name+" "+str(os.path.isfile(directory+pdf_file_name)))
        if(os.path.isfile(directory+"\\"+pdf_file_name)):
            downloaded+=1
            #source = directory + "\\"+ pdf_file_name
            #destination = dst_folder +"\\"+ pdf_file_name
            #shutil.move(source,destination)
    total=total+downloaded
    print(str(temp2['year'][ind])+" "+str(temp2['no_docs'][ind])+" "+str(temp2['issue_url'][ind])+" "+str(downloaded))

print(total)
