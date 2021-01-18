import os, sys, stat
import time
import shutil
from pathlib import Path
from flask import Flask, request, render_template, jsonify, make_response, render_template_string
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
from wtforms import Form

#from wtforms.field import Select
#SECRET_KEY = 'development'
app = Flask(__name__)
logging.basicConfig(filename="myapp.log", level=logging.INFO)

### Old definition, may be used in future
devices_dict = {}
reload_content = {}
result = ''
###

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
    def __init__(self, templatesPath, configuredIOCPath):
        dict.__init__(self, templatesPath = templatesPath, configuredIOCPath= configuredIOCPath)
        self.templatesPath = templatesPath
        self.configuredIOCPath= configuredIOCPath
        
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
            st_cmd_file_path = findfile(self.configuredIOCPath+"/"+str(i), "st.cmd")
            with open(st_cmd_file_path, 'r+', encoding='utf-8') as f:
                for line in f:
                    if "ADDR" in line:
                        address = line[-4:-2]
            item = dict(name=name, address=address)
            items_list.append(item)                                 
            #items_list.append({"ioc:":item, "address":address})
        print(items_list)            
        return items_list
    
    def getObj(self, iocname):
        items_list = [] 
        if "*" in iocname:
            iocname=iocname[1:]
        configuredIOCPath = "/home/pi/ConfiguredIOC"
        path = str(configuredIOCPath) + "/" + str(iocname) + "/iocBoot/iocgpib"
    
        st_cmd_file_path = findfile(configuredIOCPath+"/"+str(iocname), "st.cmd")
        print(st_cmd_file_path)
        with open(str(st_cmd_file_path)) as f:
            for line in f:
                if "ADDR" in line:
                    address = line[-4:-2]
        item = dict(name=iocname, address=address)
        items_list.append(item)
        print(items_list)
        return items_list
    
    def getConfiguredIOC(self):
        list_dir = os.listdir(self.configuredIOCPath)
        items_list = []        
        for i in list_dir:
            print(i)
            path = str(self.configuredIOCPath) + "/" + str(i) + "/iocBoot/iocgpib"
            status = self.checkIOCstatus(path)
            mark = self.getMark(status)
            item = dict(description=mark + i)
            items_list.append(item)            
        print(items_list)            
        return items_list
    
    def findfile(start, name):
        for relpath, dirs, files in os.walk(start):
            if name in files:
                full_path = os.path.join(start, relpath, name)
                return os.path.normpath(os.path.abspath(full_path))


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

        
@app.route('/',methods=['GET' ,'POST'])
def open_index():
    i = IOCS("/home/pi/Templates/Keithley","/home/pi/ConfiguredIOC")
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]

    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())


@app.route('/selected',methods=['GET' ,'POST'])
def selected():
    i = IOCS("/home/pi/Templates/Keithley","/home/pi/ConfiguredIOC")
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    print(request.form["iocname"])
    print(request)
    print(request.args.get("iocname"))

    
    if request.method == 'POST':
        as_dict =reuest.form.getList("configuredIOC")
      
        print(request.args.get("iocname"))
        if 'action' in request.form:
            if request.form['action'] == 'start':
                try:
                    logging.info('get address {}, pv name {}, {}'.format(address_input, pvname_input, time.asctime(time.localtime(time.time()))))
                    print("start IOC {}".format(address_input))
                    dst = "/home/pi/ConfiguredIOC"
                    i = IOCS("/home/pi/Templates/Keithley","/home/pi/ConfiguredIOC")
                    path = dst + "/" + "gpib_test" + "/iocBoot/iocgpib"
                    print(path)
                    i.openIOC(path)
                   
                    #process = subprocess.run(command_line_args, shell=True, cwd=path)
                    #output = process.stdout
                    print("app is run")
                except:
                    render_template('error.html')
            else:
                return("NO action: getAddress")
        else:
            return("NO action")
  
   

    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())


def runApp(dst):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./st.cmd"
    path = dst + "/gpib_test/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
    



### Configure the address and pv name
@app.route('/configure', methods=['GET', 'POST'])
def configure():
    address_input = request.form.get('comp_select')
    pvname_input = request.form['pv_name']
    if pvname_input:
        print("pvname: ", pvname_input)    
        if request.method == 'POST':
            print(request.form)
            if 'action' in request.form:
                if request.form['action'] == 'getAddress':
                    try:
                        logging.info('get address {}, pv name {}, {}'.format(address_input, pvname_input, time.asctime(time.localtime(time.time()))))
                        print("get Address {}".format(address_input))
                        dst = DST
                        src = SRC
                        configure_parameters = {"address": str(address_input), "pvname": str(pvname_input)}
                        copyTemplates(src, dst)
                        print("copyTemplates")
                        configure(configure_parameters, dst)
                        print("Configure Done")
                        #runApp(dst)
                        print("app is run")
                    except:
                        render_template('error.html')
                else:
                    return("NO action: getAddress")
            else:
                return("NO action")
        else:
            return("No POST method")
                    
    else:
        logging.info('PV Name: NO INPUT. {}'.format(address_input, pvname_input, time.asctime(time.localtime(time.time()))))
        return("PV Name: NO INPUT. Please give an input. ")

    return render_template('keithley2000.html', data=str(address_input), name=str(pvname_input), devices=devices_dict, result=result, reload_content=reload_content)

def configure(parameter_dict, dst):
    for i in parameter_dict.keys():
        print(i)
        if i == "address":
            configureAddress(parameter_dict['address'], dst)
        elif i == "pvname":
            configurePV(parameter_dict['pvname'], dst)
        else:
            pass
            
def configureAddress(address, dst):
    print("configureAddress: ", address) 
    file_path = dst + "/gpib_test/iocBoot/iocgpib/st.cmd"
    changePermission(file_path)
    content_search = "ADDR="
    new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"\n' % str(address)
    changeContent(file_path, content_search, new_line)
    
def configurePV(pvname, dst):
    print("pvname input: ", pvname)
    print("configurePV: ", pvname) 
    file2 = dst + "/gpib_test/iocBoot/iocgpib/envPaths"
    changePermission(file2)
    line2 = 'epicsEnvSet("IOC",%s)\n' % pvname
    content2 = "IOC"
    changeContent(file2, content2, line2)

    file3 = dst + "/gpib_test/iocBoot/iocgpib/envPaths"
    top_path = dst + "/gpib_test"
    changePermission(file3)
    line3 = 'epicsEnvSet("TOP", %s)\n' % top_path
    content3 = "TOP"
    changeContent(file3, content3, line3)
        
def runApp(dst):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./st.cmd"
    path = dst + "/gpib_test/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
    
def changeContent(src, content_search, new_line):
    print("change file: {}".format(src))
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(src, "w", encoding="utf-8") as f_w:
        for line in lines:
            if content_search in line:
                line=line.replace(line, new_line)            
            f_w.write(line)
            
def copyTemplates(src, dst):
    if Path(dst).is_dir():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)      
    print("src is copied in dst " ) 
    
def changePermission(src):
    shutil.chown(src, user="pi", group="pi")
    os.chmod(src, stat.S_IRUSR+stat.S_IWUSR+stat.S_IXUSR+stat.S_IRGRP+stat.S_IWGRP+stat.S_IXGRP)

@app.route('/result', methods=['GET', 'POST'])
def result():
    dst = DST
    print(request.form)
    if request.method == 'POST':
        print(request.form)
        if 'action' in request.form:
            if request.form['action'] == 'startIOC':
                result= "ok"
                try:
                    runApp(dst)
                except:
                    render_template('error.html')
            elif request.form['action'] == 'stopIOC':
                result= "stop"
                try:
                    closeApp(dst)
                except:
                    render_template('error.html')
            elif request.form['action'] == 'ok':
                return "add new IOC ok"
            elif request.form['action'] == 'cancel':
                return "cancel"
            else:
                return("No action executed")
        else:
                return("NO action form")
    
    return render_template('result.html', devices=devices_dict, result=result, reload_content=reload_content )
def runApp(dst):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./external_start"
    path = dst + "/gpib_test/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
def closeApp(dst):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./external_stop"
    path = dst + "/gpib_test/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success

@app.route('/<name>', methods=['GET', 'POST'])
def getIOC(name):
    i = IOCS("/home/pi/Templates/Keithley","/home/pi/ConfiguredIOC")
    name= i.getObj(name)
    for item in name:
        result = item
    return jsonify(result)
@app.route('/form', methods=['GET', 'POST'])
def form():
     if request.method == 'POST':
            print(request.form)
            if 'action' in request.form:
                if request.form['action'] == 'showInfo':
                    string_tem = """
{% extends "index.html" %}
{% block content %}
                        <h1>set ioc</h1>
                        <form>

                        <div> {{ info }}</div>
                        <button>submit</button>
                        </form>
{% endblock %}


"""
                    return render_template_string(string_tem)
                    
if __name__ == "__main__":
    app.run(host='192.168.1.101', port='8080', threaded=True)
