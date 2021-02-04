import os, sys, stat
import time
import shutil
from pathlib import Path
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
import json


def listfiles(path):
    return os.listdir(path)

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
        self.templatesPath = "/home/pi/Templates/Keithley/keithley2000"
        self.configuredIOCPath= "/home/pi/ConfiguredIOC"
        self.parameter_file= "parameters.json"
        
    def getConfiguredIOC(self):
        list_dir = os.listdir(self.configuredIOCPath)
        items_list = []
        
        for i in list_dir:
            #print(i)
            path = str(self.configuredIOCPath) + "/" + str(i) + "/iocBoot/iocgpib"
            if os.path.isdir(path):
                status = self.checkIOCstatus(path)
                mark = self.getMark(status)
                item = dict(name=mark + i)
                items_list.append(item)
            else:
                pass
        #print(items_list)            
        return items_list
        
    def getTemplates(self):
        list_dir = os.listdir(self.templatesPath)
        items_templates = []
        for i in list_dir:
            item = dict(name=i)
            items_templates.append(item)  
        return items_templates
    
    def getObjParameters_list(self, obj_name, path):
        path_parameters= path + "/" + str(obj_name) + "/" + self.parameter_file
        print(path_parameters)
        f = open(path_parameters,)
        data = json.load(f)
        data_list = []
        #print(data)
        for i in data:
            print(i)
            print(data[i])
            dict_item = {i:data[i]}
            
            data_list.append(dict_item)
        f.close()
        print(data_list)
        return data_list
       
### get parameters from the file, second try
    def getObjParameters(self, obj_name, path):
        if obj_name in listfiles(path):
            if os.path.isdir(path + "/" + str(obj_name)):
                path_parameters= path + "/" + str(obj_name) + "/" + self.parameter_file
                print(path_parameters)
                f = open(path_parameters,)
                data = json.load(f)
                print("parameters file content: ", data)
                return data['device']
            else:
                print("Path Error: ", path + "/" + str(obj_name))
                return None
                
        else:
            print(obj_name + " is not under the path: " + path)
            return None
###

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

### get parameters from the content, first try    
    def getObj_parameters(self, iocname, path):
        if "*" in iocname:
            iocname_real=iocname[1:]
        else:
            iocname_real=iocname
        print(iocname_real)
        parameters_file = self.getObjParameters(iocname_real, path)
    
        items_list = [] 
        print(parameters_file)
        return parameters_file

    def getObj(self, iocname):
        items_list = [] 
        if "*" in iocname:
            iocname_real=iocname[1:]
        else:
            iocname_real=iocname
        parameters_file = self.getObjParameters(iocname_real, self.configuredIOCPath)
        if parameters_file:
            print(parameters_file)
            status = self.checkIOCstatus("/home/pi/ConfiguredIOC"+ "/" + str(iocname_real) + "/iocBoot/iocgpib")
            mark = self.getMark(status)
  
            if mark == "*":
                ioc_status = "running"
                possible_operation = "Stop"
            else:
                ioc_status = "idle"
                possible_operation = "Start"
            configuredIOCPath = "/home/pi/ConfiguredIOC"
            PVname = parameters_file['pvname']
            Address = parameters_file['address']
            item = dict(name=iocname_real, address=Address, status=ioc_status, operation=possible_operation, pvname=PVname)
            items_list.append(item)
            print("Get Obj: ", items_list)
        else:
            pass
    #path = str(configuredIOCPath) + "/" + str(iocname_real) + "/iocBoot/iocgpib"
    #if os.path.isdir(path):
        #st_cmd_file_path = findfile(configuredIOCPath+ "/" +str(iocname_real), "st.cmd")
        #print(st_cmd_file_path)
        #with open(str(st_cmd_file_path)) as f:
            #for line in f:
                #if "ADDR" in line:
                    #address = line[-4:-2]
       
        #item = parameters_file
        #item.update(status=ioc_status)
        #item.update(operation=possible_operation)
        #item = dict(name=iocname_real, address=Address, status=ioc_status, operation=possible_operation, pvname=PVname)
            
        return items_list
###
    
    def getTemplateObj(self, iocname):
        items_list = [] 
        path = str(self.templatesPath) + "/" + str(iocname) + "/iocBoot/iocgpib"
        if os.path.isdir(path):
            st_cmd_file_path = findfile(self.templatesPath+ "/" +str(iocname), "st.cmd")
            with open(str(st_cmd_file_path)) as f:
                for line in f:
                    if "ADDR" in line:
                        address = line[-4:-2]
            item = dict(name=iocname, address=address)
            items_list.append(item)
            print("Get Obj: ", items_list)
        return items_list
    
    

    def checkIOCstatus(self, path):
        command_line_args = "./external_status"
        if os.path.isdir(path):
            process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
            with process.stdout:
                log_subprocess_output(process.stdout)
            exitcode = process.wait()
            return exitcode
        else:
            return "error"
      
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
        
    def configureFile(self,data, path):
        with open(path, "w") as f:
            json.dump(data, f)
            
        
#i = IOCS()
#i.getObj("test")

