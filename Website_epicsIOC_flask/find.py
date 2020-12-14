                            
import os
import shutil
def search_file(path,str):
    for x in os.listdir(path):
        next_path=os.path.join(path,x)
        if os.path.isfile(next_path):
            if str in x:
                print(os.path.relpath(next_path, p))
        else:
            search_file(next_path,str)
#p=input('input search path：')
#str=input('input search str of the file name：')
#search_file(p,str)
def copyTemplates(src, dst):
    shutil.copytree(src, dst)




def findContentFile(src, content):
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(src, "w", encoding="utf-8") as f_w:
        for line in lines:
            if content in line:
                line=line.replace(line, 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=20" ')
            
            f_w.write(line)

if __name__== '__main__':
    copyTemplates("Templates/Keithley/keithley2000", "copyTemplatesDestination")
    findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=19")
   


