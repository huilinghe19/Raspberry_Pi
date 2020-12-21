
from flask import Flask, request, render_template
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
#import GPIB_Server_Functions as ServerGPIB 

import os, sys, stat
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
import shutil
from pathlib import Path

#SECRET_KEY = 'development'
app = Flask(__name__)

logging.basicConfig(filename="myapp.log", level=logging.INFO)

### Old definition, may be used in future
devices_dict = {}
reload_content = {}
result = ''
address = ""
pvname = ""
SRC = "/home/pi/Templates/Keithley/keithley2000"
DST = "/tmp/newIOC"
address_list = [{'address':'19'}, {'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'},  {'address':'28'}, {'address':'29'}, {'address':'30'}, {'address':'31'}]
#CONFIGURE_PARAMETERS = [{"address": ''}, {"pvname": ''}]
###

def copyTemplates(src, dst):
    shutil.copytree(src, dst)      
    print("src: is copied in dst: " ) 

@app.route('/hello',methods=['post','get'])
def hello_world():
    return render_template('example.html',data=[{'address':'19'}])

@app.route('/test',methods=['post','get'])
def test():
    select = request.form.get('comp_select')
    return(str(select))



@app.route('/',methods=['GET' ,'POST'])
def open_index():
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, data=address_list)


### Webpage for Keithley 2000
@app.route('/openKeithley2000IOC', methods=['GET', 'POST'])
def openKeithley2000IOC():
    address = request.form.get('comp_select')
    pvname = request.form['pv_name']
    print(pvname)
    print(address)
    if request.method == 'POST':
        print(request.form)
        if 'action' in request.form:
            if request.form['action'] == 'getAddress':
                print("get Address {}".format(address))

                #configure("address")
                #configure("pvname")
                dst = DST
                src = SRC
                file_path = dst + "/gpib_test/iocBoot/iocgpib/st.cmd"
                changePermission(file_path)
                content_search = "ADDR="
                new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"\n' % str(address)
                changeContent(file_path, content_search, new_line)

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
                result="OK"
                print("Configure Done")
                
                
                runApp(address, dst)  
    return render_template('keithley2000.html', data=str(address), name=str(pvname), devices=devices_dict, result=result, reload_content=reload_content)

def configure(parameter):
    print(paramater)
    
def runApp(address, dst):
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
    shutil.copytree(src, dst)      
    print("src: is copied in dst: " ) 
    
def changePermission(src):
    shutil.chown(src, user="pi", group="pi")
    os.chmod(src, stat.S_IRUSR+stat.S_IWUSR+stat.S_IXUSR+stat.S_IRGRP+stat.S_IWGRP+stat.S_IXGRP)







if __name__ == "__main__":
    copyTemplates(SRC, DST)
    #app.run(host='134.30.36.95', port='8080', threaded=True)
    app.run(host='192.168.1.101', port='8080', threaded=True)
