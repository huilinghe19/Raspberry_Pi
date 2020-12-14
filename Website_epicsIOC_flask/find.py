                            
import os
import shutil
from pathlib import Path


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


def choose_connection(input):
    connection_dict = {"EPICS_IOC":"iocgpib",
                       "GPIB_ADDRESS": "19",
                       "connection": "GPIB",
                       }
    if input == connection_dict["connection"]:
       print("connect with GPIB")
       
       
    else:
        print("connect with Serial Line")

def show_GPIBTemplates():
    search_path = "/home/pi/Templates/Keithley"
    input = "keithley2000"
    str = search_path + "/" + input
    #my_dir = Path(str)
    if Path(str).is_dir():
        print(str + ": Dir is TRUE")
    else:
        print(str + ": Dir does not exist")
        
def findContentFile(src, content_search, new_line):
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(src, "w", encoding="utf-8") as f_w:
        for line in lines:
            if content_search in line:
                line=line.replace(line, new_line)
            
            f_w.write(line)
def openIOC():
    print("open IOC")

def main():
    choose_connection("GPIB")
    show_GPIBTemplates()
    templates_path = "Templates/Keithley/keithley2000"
    destination_path = "copyTemplatesDestination"
    copyTemplates(templates_path , destination_path)
    findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=19"')
    #findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/envPaths", 'epicsEnvSet("IOC" ', 'epicsEnvSet("IOC","keithley2000_test") ')
    openIOC()

if __name__== '__main__':
    main()    

