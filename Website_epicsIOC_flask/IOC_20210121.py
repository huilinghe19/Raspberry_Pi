import os, sys, stat
import time
import shutil
from pathlib import Path
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging


SRC = "/home/pi/Templates/Keithley/keithley2000"
DST = "/tmp/newIOC"
#DST= "/home/pi/configuredIOC"
address_list = [{'address':'19'}, {'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'},  {'address':'28'}, {'address':'29'}, {'address':'30'}, {'address':'31'}]

#items = [dict(name='*', description='test'),
             #dict(name=' ', description='test1'),
             #dict(name='*', description='test2')]
#items_templates = [dict(description='Keithley2000'),
             #dict(description='keithley3000')]

def findfile(start, name):
    for relpath, dirs, files in os.walk(start):
        if name in files:
            full_path = os.path.join(start, relpath, name)
            return os.path.normpath(os.path.abspath(full_path))
      
def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''):  # b'\n' -seperated lines
        logging.info('got line from subprocess:%r', line)

class IOCS(dict):
    def __init__(self):
        dict.__init__(self)
        self.templatesPath = "/home/pi/Templates/Keithley"
        self.configuredIOCPath= "/home/pi/ConfiguredIOC"
        
    def getTemplates(self):
        list_dir = os.listdir(self.templatesPath)
        items_templates = []
        for i in list_dir:
            print(i)
            item = dict(description=i)
            items_templates.append(item)  
        return items_templates
    
    def getIOCObject(self):
        list_dir = os.listdir(self.configuredIOCPath)
        items_list = []        
        for i in list_dir:
            print(i)
            path = str(self.configuredIOCPath) + "/" + str(i) + "/iocBoot/iocgpib"
            status = self.checkIOCstatus(path)
            mark = self.getMark(status)
            name = mark + i  
            st_cmd_file_path = findfile(self.configuredIOCPath + "/" +str(i), "st.cmd")
            with open(st_cmd_file_path, 'r+', encoding='utf-8') as f:
                for line in f:
                    if "ADDR" in line:
                        address = line[-4:-2]
            item = dict(name=name, address=address)
            items_list.append(item)                                 
        print(items_list)            
        return items_list
    
    def getObj(self, iocname):
        if "*" in iocname:
            iocname_real=iocname[1:]
        else:
            iocname_real=iocname
        status = self.checkIOCstatus("/home/pi/ConfiguredIOC"+ "/" + str(iocname_real) + "/iocBoot/iocgpib")
        mark = self.getMark(status)
        items_list = [] 
        if mark == "*":
            ioc_status = "running"
            possible_operation = "stop"
         
        else:
            ioc_status = "idle"
            possible_operation = "start"
        configuredIOCPath = "/home/pi/ConfiguredIOC"
        path = str(configuredIOCPath) + "/" + str(iocname_real) + "/iocBoot/iocgpib"
    
        st_cmd_file_path = findfile(configuredIOCPath+ "/" +str(iocname_real), "st.cmd")
        #print(st_cmd_file_path)
        with open(str(st_cmd_file_path)) as f:
            for line in f:
                if "ADDR" in line:
                    address = line[-4:-2]
        item = dict(name=iocname_real, address=address, status=ioc_status, operation=possible_operation)
        items_list.append(item)
        print("Get Obj: ", items_list)
        return items_list
    
    def getTemplateObj(self, iocname):
        path = str(self.templatesPath) + "/" + str(iocname) + "/iocBoot/iocgpib"
        st_cmd_file_path = findfile(self.templatesPath+ "/" +str(iocname), "st.cmd")
        items_list = [] 
        with open(str(st_cmd_file_path)) as f:
            for line in f:
                if "ADDR" in line:
                    address = line[-4:-2]
        item = dict(name=iocname, address=address)
        items_list.append(item)
        print("Get Obj: ", items_list)
        return items_list



       
    def getConfiguredIOC(self):
        list_dir = os.listdir(self.configuredIOCPath)
        items_list = []        
        for i in list_dir:
            #print(i)
            path = str(self.configuredIOCPath) + "/" + str(i) + "/iocBoot/iocgpib"
            status = self.checkIOCstatus(path)
            mark = self.getMark(status)
            item = dict(description=mark + i)
            items_list.append(item)            
        print(items_list)            
        return items_list

    def checkIOCstatus(self, path):
        command_line_args = "./external_status"
        process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()
        return exitcode
      
    def getMark(self, status):
        print("status: ".format(status))
        if status  == 0:
            result = "*"
        elif status == 1:
            result = " "   
        else:
            result = "error"
        print(result)
        return result
    
    def openIOC(self,path):
        command_line_args = "./external_start"
        process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()
        return exitcode
    
    def stopIOC(self, path):
        command_line_args = "./external_stop"
        process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()
        return exitcode
    
    def openObj(self,obj):
        command_line_args = "./external_start"
        path = str(self.configuredIOCPath) + "/" + str(obj) + "/iocBoot/iocgpib"
        process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()
        return exitcode
    
    def closeObj(self,obj):
        command_line_args = "./external_stop"
        path = str(self.configuredIOCPath) + "/" + str(obj) + "/iocBoot/iocgpib"
        process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
        with process.stdout:
            log_subprocess_output(process.stdout)
        exitcode = process.wait()
        return exitcode
    
    def removeObj(self,obj):
        path = str(self.configuredIOCPath) + "/" + str(obj) 
        shutil.rmtree(path, ignore_errors=False)

        
i = IOCS()
i.getTemplateObj('keithley2000')
