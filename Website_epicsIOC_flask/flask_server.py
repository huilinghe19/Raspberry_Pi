
import os, sys, stat
import time
import shutil
from pathlib import Path
from flask import Flask, request, render_template
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
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

SRC = "/home/pi/Templates/Keithley/keithley2000"
DST = "/tmp/newIOC"
address_list = [{'address':'19'}, {'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'},  {'address':'28'}, {'address':'29'}, {'address':'30'}, {'address':'31'}]


@app.route('/',methods=['GET' ,'POST'])
def open_index():
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, data=address_list)

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
                        configure_parameters = {"address": address_input, "pvname": pvname_input}
                        copyTemplates(src, dst)
                        configure(configure_parameters, dst)
                        print("Configure Done")
                        #runApp(dst)
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
            else:
                return("NO action: startIOC")
        else:
                return("NO action")
    
    return render_template('result.html', devices=devices_dict, result=result, reload_content=reload_content )
def runApp(dst):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./st.cmd"
    path = dst + "/gpib_test/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
    

if __name__ == "__main__":    
    app.run(host='192.168.1.101', port='8080', threaded=True)
