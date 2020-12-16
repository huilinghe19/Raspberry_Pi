
from flask import Flask, request, render_template
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
#import GPIB_Server_Functions as ServerGPIB 

import os, sys, stat
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging


#SECRET_KEY = 'development'
app = Flask(__name__)

logging.basicConfig(filename="myapp.log", level=logging.INFO)

### Old definition, may be used in future
devices_dict = {}
reload_content = {}
result = ''
###


@app.route('/hello',methods=['post','get'])
def hello_world():
    return render_template('example.html',data=[{'address':'19'}, {'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, {'address':'6'}, {'address':'7'}])

@app.route('/test',methods=['post','get'])
def test():
    select = request.form.get('comp_select')
    return(str(select))



@app.route('/',methods=['GET' ,'POST'])
def open_index():  
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, 
	data=[{'address':'19'}, {'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'},  {'address':'28'}, {'address':'29'}, {'address':'30'}, {'address':'31'}])
### Webpage for Keithley 2000
@app.route('/openKeithley2000IOC', methods=['GET', 'POST'])
def openKeithley2000IOC():
    address = request.form.get('comp_select')
    if request.method == 'POST' :
        print(request.form)
        if 'action' in request.form:
            if request.form['action'] == 'getAddress':
                print("get Address {}".format(address))
                #configureIOCfiles(address)
                new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"' % str(address)
                print(new_line)
                findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", new_line)
                runApp(address)
                #new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR={}"'.format(str(address))
                #findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", new_line)
                #return render_template('keithley2000.html', data=str(address), devices=devices_dict, result=result, reload_content=reload_content)
                #new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR={}"'.format(address)
                #file = "/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd"
                #os.chmod(file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR )
                #os.chmod(file, stat.S_IXGRP)
                #os.chmod(file, stat.S_IWOTH)
                #findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", new_line)
                #return render_template('keithley2000.html', data=str(address), devices=devices_dict, result=result, reload_content=reload_content)
            #if request.form['action'] == 'startIOC':
                #address = request.form.get('comp_select')
                #print(" Address {}".format(address))
                #findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=20"')
                #print("start IOC")
                #runApp(address)                
    return render_template('keithley2000.html', data=str(address), devices=devices_dict, result=result, reload_content=reload_content)
def runApp(address):
    print("start IOC")
    print(str(address))
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./st.cmd"
    process = subprocess.run(command_line_args, shell=True, cwd="/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib")
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
def configureIOCfiles(address):
    new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"' % str(address)
    print(new_line)
    findContentFile("/home/pi/copyTemplatesDestination/gpib_test/iocBoot/iocgpib/st.cmd", "ADDR=", new_line)
def findContentFile(src, content_search, new_line):
    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(src, "w", encoding="utf-8") as f_w:
        for line in lines:
            if content_search in line:
                line=line.replace(line, new_line)            
            f_w.write(line)



### Webpage for Keithley 3000, just for testing other devices in future 
#@app.route('/openKeithley3000IOC', methods=['GET' ,'POST'])
#def open_keithley3000ioc():
#    if request.method == 'POST' :
#        logging.info('open keithley3000 IOC... {}'.format(time.asctime(time.localtime(time.time()))))
#        #runApp() 
#    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content)
#def runApp():
#    
#    command_line_args = "./st.cmd"
 #   process = subprocess.run(command_line_args, shell=True, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
 #   output = process.stdout
 #   logging.info('runApp: Keithley 3000 IOC is Started. {}'.format(time.asctime(time.localtime(time.time()))))


if __name__ == "__main__":    
    #app.run(host='134.30.36.95', port='8080', threaded=True)
    app.run(host='192.168.1.101', port='8080', threaded=True)
