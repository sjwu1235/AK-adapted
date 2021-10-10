import os
import shutil
import earthpy as et

def setHomeDirectory():
    if os.path.exists(et.io.HOME):
     et.io.HOME
    else:
        print("Home directory not found")
        
# Create the directory Staging for storage of pdfs
def createTempStorage():
    setHomeDirectory()
    path=os.path.join(os.getcwd(),'TempStorage')
    try: 
        os.mkdir(path)
    except OSError as error:    
        print(error) #Should include something else here to do if there is an error ? Maybe prompt user to rename the directory they have with the same name 

def setTempStorage():
    setHomeDirectory()
    path=os.path.join(os.getcwd(),'TempStorage')
    if os.path.exists(path):
     os.chdir(path)
    else:
        print("Temp Storage directory not found")

def createStorageDirectory():
    setHomeDirectory()
    storagepath=os.path.join(os.getcwd(),'Storage')
    try: 
        os.mkdir(storagepath)
    except OSError as error:    
        print(error) #Should include something else here to do if there is an error ? Maybe prompt user to rename the directory they have with the same name 

def moveFilesToStorage():
    setHomeDirectory()
    storagepath=os.path.join(os.getcwd(),'Storage')
    setTempStorage()
    files=os. listdir()
    for f in files:
        shutil.move(f, storagepath)
    
def deleteStaggingFiles():
    setTempStorage()
    files=os.listdir()
    for f in files:
        os.remove(f)
    #Add a check here to see if all files were deleted using os.listdir()
    
def deleteTempStorage():
    setHomeDirectory()
    path=os.path.join(os.getcwd(),'TempStorage')
    path2=os.path.join(os.getcwd(),'Storage')
    os.rmdir(path)
    os.rmdir(path2)