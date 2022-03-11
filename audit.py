from encodings import utf_8
from pickle import FALSE
import pandas as pd
import re
import os

# Importing BeautifulSoup class from the bs4 module
from bs4 import BeautifulSoup

#Helper function for a specific tag
def ref2_processor(k, tag2, temp):
    s=k.text.replace('\xa0', ' ').split(',')
    print(s)
    print(s[1])
    temp[1]=tag2.find_all('span',class_='txtBold')[0].text
    temp[2]= s[0].split(')')[1].strip()
    if ('p.' not in s[1]):
        temp[3]=s[1].split(' ')[1]
        if (len(s[1].split(' '))>2):
            temp[4]=s[1].split(' ')[2].strip()[1:-1]
    temp[5]=s[0].split(')')[0][1:]
    temp[6]=s[-1].split('. ')[1] 
    return temp

#processing a single html SCOPUS file
def process_file(Parse, data):
    all_cont_tags=Parse.find_all("div", class_="container")
    j=0
    for tag in all_cont_tags:
        i=0
        temp=[None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        temp[11]=re.search('Type:(.*?)Publication',tag.text).group(1)
        
        all_div_tags=tag.find_all('div',class_="margin: 0px 0px 13px 0px")
        for tag2 in all_div_tags:
            if (len(tag2)==0):
                i+=1
                continue
            if (i==0):           
                print(j)
                j+=1
                ls=tag2.find_all('span',class_='txt')
                if (re.search('DOI:', str(tag2))):
                    temp[7]=ls[-1].text
                    if (len(ls)>2):
                        temp[0]=re.sub('<.+?>','', str(ls[0]).replace('<sup>','--').replace('</sup>','--').replace(' , ', '\n'))
                        ref2_processor(ls[1], tag2, temp)
                    else:
                        ref2_processor(ls[0], tag2, temp)
                else:
                    if (len(ls)>1):
                        temp[0]=re.sub('<.+?>','', str(ls[0]).replace('<sup>','--').replace('</sup>','--').replace(' , ', '\n'))
                        ref2_processor(ls[1], tag2, temp)
                    else:
                        ref2_processor(ls[0], tag2, temp)
            elif (i==1):
                temp[8]='\n'.join(str(tag2).replace('\xa0','').replace('<sup>','').replace('</sup>','--').split('<br/>')[1:-1])
            elif (i==2):
                temp[9]=tag2.find_all('span',class_="txt")[0].text               
            elif (i==3):
                temp[13]=tag2.find('span', class_="txt").text
            elif (i==4):
                temp[12]=tag2.find('span', class_="txt").text
            elif (i==5):
                ref=[]
                for x in tag2.find_all('td'):
                    if len(x.text)>0:
                        ref2=[]
                        for k in x.find_all('span'):
                            ref2.append(k.text)
                        ref.append('|'.join(ref2).replace('\xa0',' '))
                temp[10]='--\n'.join(ref)
            i+=1
            
        data=data.append(pd.Series(temp, index=data.columns), ignore_index=True)
    
    return data

cols=['authors', 'title', 'journal', 'volume', 'issue', 'year', 'pages', 'DOI','affiliations','abstract', 'citations','document type', 'index keywords', 'author keywords']
temp=[None, None, None, None, None, None, None, None, None, None, None, None, None]
data=pd.DataFrame(columns=cols)

for x in os.listdir("C:\\Users\\sjwu1\\Journal_Data\\Scopus\\RES"):
    if x.endswith(".html"):
        # Prints only text file present in My Folder
        print(x)
        # Opening the html file
        HTMLFile = open("C:\\Users\\sjwu1\\Journal_Data\\Scopus\\RES\\"+x, encoding='utf8')    
        # Reading the file
        index = HTMLFile.read()
        # Creating a BeautifulSoup object and specifying the parser
        Parse = BeautifulSoup(index, 'lxml')
        # data=data.append(pd.Series([int(temp), None, None, None, stable_url, Jstor_issue_text, input_deets["journal_name"], None, None], index=data.columns), ignore_index=True )
        data=process_file(Parse, data)


data.to_excel('output2.xlsx', index=False)



'''
# other sections eg: funding, publisher name, ISSN publication stage etc.
    i=0
    for tag2 in tag.find_all('div',class_="margin: 13px 0px 0px 0px"):
        if len(tag2.contents) > 0:
            if (i==0):
                print(tag2.text)
                print('\n')
                i+=1
'''