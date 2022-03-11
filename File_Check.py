import json
from pathlib import Path
import time
import pandas as pd
import os.path
import shutil
import os

directory = "..\\Path\\to\\journal\\data"    
temp = pd.read_excel("..\\path\\to\\masterlist_name.xlsx")
temp2 = pd.read_excel("..\\path\\to\\name_pivots.xlsx")

#src_folder = r"C:\Users\sjwu1\Journal_Data"
#dst_folder = r"C:\Users\sjwu1\Master_\AER_data"

total=0
fulllist_s_1940=0
for ind in temp2.index:
    temp3=temp[temp['issue_url']==temp2['issue_url'][ind]]
    downloaded=0
    for ind2 in temp3.index:
        pdf_file_name=temp['stable_url'][ind2].split('/')[-1]+".pdf"
        if (temp2['year'][ind]>=1940):
            fulllist_s_1940+=1
        #print(pdf_file_name+" "+str(os.path.isfile(directory+pdf_file_name)))
        if(os.path.isfile(directory+"\\"+pdf_file_name)):
            downloaded+=1
            #source = directory + "\\"+ pdf_file_name
            #destination = dst_folder +"\\"+ pdf_file_name
            #shutil.move(source,destination)
    total=total+downloaded
    print(str(temp2['year'][ind])+" "+str(temp2['no_docs'][ind])+" "+str(temp2['issue_url'][ind])+" "+str(downloaded))

print(total)
print(fulllist_s_1940)
