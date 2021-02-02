import os, sys, stat
import time
import shutil
import requests
from pathlib import Path
from flask import Flask, request, render_template, jsonify, make_response, render_template_string, redirect, url_for
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
import IOC
from IOC import IOCS
import json

#SECRET_KEY = 'development'
app = Flask(__name__)
#logging.basicConfig(filename="myapp.log", level=logging.INFO)

### Old definition, may be used in future
devices_dict = {}
reload_content = {}
result = ''
###
SRC = "/home/pi/Templates/Keithley/keithley2000/gpib_test"
TEMPLATE_PATH = "/home/pi/Templates/Keithley/keithley2000/"
DST = "/home/pi/ConfiguredIOC"

        
@app.route('/',methods=['GET' ,'POST'])
def index():
    I = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content,
                           headers = headers, objects = I.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = I.getTemplates())

@app.route('/add', methods=['GET', 'POST'])
def add():
    I = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    print("choose template : ", request.form['templateChosen'])
    chosenTemplate=request.form['templateChosen']
    data = I.getObj_parameters(chosenTemplate, "/home/pi/Templates/Keithley/keithley2000")
    print(data.keys())
    #newdev= data['name']
    #pvname= data['pvname']
    parameters_list = []
    if 'address' in data.keys():
        address = data['address']
        array = [{'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'19'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'}, {'address':'28'}, {'address':'29'}, {'address':'30'}]
        element = {'address':str(address)}
        if element in array:
            array.remove(element)
        array.insert(0, element)
        address_list = array   
    if request.method == 'POST':
        print("Request:", request.form)
        if 'action' in request.form:
            if request.form['action'] == 'add':
                try:
                    html = """
<div style="position:absolute; left:30%">
<table style="border:1px solid black;">
<tr>
<td style="border:1px solid black;">

<table>
<b>Adding a new device IOC</b>
 <br/>
<form class="form-inline" method="POST" action="{{ url_for('configure')}}">
 <input type="hidden" name="templateChosen" id="templateChosen" value="{{ chosenTemplate}}">"""
                    for i in data.keys():
                        parameters_list.append(i)
                        parameters_list.append(data[i])
                        
                        if i !="address":
                            html += """

<div class="input-text">
<label for="%s">%s</label>

<input type="text" id="%s" name="%s" value="%s">
 <br/>   
</div>

"""%(i, i, i, i, data[i])
                    html += """

  <div class="form-group">
    <div class="input-group">
    
        <span class="input-group-addon">GPIB Address </span>
            <select name="address" class="selectpicker form-control">
              {% for o in data %}
              <option value="{{ o.address }}">{{ o.address }}</option>
              {% endfor %}
            </select>
    </div>
</div>
<button type="submit" onclick="start_loading_animation(this) class="btn btn-default" name="action" value="configure">OK</button>
  </div>
</form>
</form>
<form class="form-inline" method="POST" action="{{ url_for('index')}}">
<button type="submit" class="btn btn-default" name="action" value="home" onclick="start_loading_animation(this)" >Cancel</button>
</form>

     </div>
     </table>
</td>
</tr>
</table>
</div>
"""
                    print(html)
                    return render_template_string(html,  data=address_list, chosenTemplate=chosenTemplate)
                   
                except:
                    render_template('error.html')
            else:
                return("NO action: add")
        else:
            return("NO action")
    return render_template('addnewioc.html',devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = I.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = I.getTemplates())
def getConfigureFile(file):
    with open(file) as json_file:
        data = json.load(json_file)
        for i in data['device']:
            print(i)
        return data['device']
        
def configure(parameter_dict, dst, name):
    for i in parameter_dict.keys():
        print(i)
        if i == "address":
            configureAddress(parameter_dict['address'], dst, name)
        elif i == "pvname":
            configurePV(parameter_dict['pvname'], dst, name)
        else:
            pass
            
def configureAddress(address, dst, name):
    print("configureAddress: ", address) 
    file_path = dst + "/" + name + "/iocBoot/iocgpib/st.cmd"
    changePermission(file_path)
    content_search = "ADDR="
    new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"\n' % str(address)
    changeContent(file_path, content_search, new_line)
    
def configurePV(pvname, dst, name):
    print("pvname input: ", pvname)
    print("configurePV: ", pvname) 
    file2 = dst + "/" + name + "/iocBoot/iocgpib/envPaths"
    changePermission(file2)
    line2 = 'epicsEnvSet("IOC",%s)\n' % pvname
    content2 = "IOC"
    changeContent(file2, content2, line2)

    file3 = dst  + "/" + name + "/iocBoot/iocgpib/envPaths"
    top_path = dst  + "/" + name + '/'
    changePermission(file3)
    line3 = 'epicsEnvSet("TOP", %s)\n' % top_path
    content3 = "TOP"
    changeContent(file3, content3, line3)
    
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
    shutil.chown(src, user="root", group="root")
    os.chmod(src, stat.S_IRUSR+stat.S_IWUSR+stat.S_IXUSR+stat.S_IRGRP+stat.S_IWGRP+stat.S_IXGRP)

    
### Configure the parameters
@app.route('/configure', methods=['GET', 'POST'])
def configure():
    configureDict = request.form
    IOC = IOCS()
    print(request.form)
    newdev = request.form['name']
    address_input = request.form.get('address')
    pvname_input = request.form['pvname']

    if request.method == 'POST':
        print(request.form)
        if 'action' in request.form:
            if request.form['action'] == 'configure':
                try:
                    copyTemplates(TEMPLATE_PATH + request.form.get('templateChosen') , DST + '/'+ request.form.get('name'))
                    configureNew(configureDict)
                except:
                    render_template('error.html')
            else:
                return("NO action: configure")
        else:
            return("NO action")
    else:
        return("No POST method")
    return redirect(url_for('index'))
    #render_template('keithley2000.html', data=str(address_input), name=str(pvname_input), dev = str(newdev), devices=devices_dict, result=result, reload_content=reload_content)

def configureNew(configureDict):
    for key in configureDict:
        print(key)
        value = request.form.get(key)
        if key == "name":
            newdev = request.form.get(key)
            #print("configure name: ", value)
          
        elif key=="templateChosen":
            template = request.form.get(key)
            #print("template chosen ", value)
            
        elif key == "comp_select":
            configureAddress(request.form.get('address'), DST, request.form.get('name'))
            #print("configure address ", value)
         
        elif key == "pvname":
            pvname = request.form.get(key)
            configurePV(pvname, DST, newdev)
            #print("configure PV ", value)
         
        elif key == "port":
            port = request.form.get(key)
            configurePort(value)
        elif key == "host":
            host = request.form.get(key)
            configureHost(value)
        elif key=="action":
            pass
        else:
            print("Configure the parameters in the configuration file")
        
       
      
       
        parameters = dict(device=configureDict)
        configureFile(parameters, DST + '/'+ newdev +'/'+ "parameters.json" )
def configureFile(data, path):
    with open(path, "w") as f:
        json.dump(data, f) 
    
def configure(parameter_dict, dst, name):
    for i in parameter_dict.keys():
        print(i)
        if i == "address":
            configureAddress(parameter_dict['address'], dst, name)
        elif i == "pvname":
            configurePV(parameter_dict['pvname'], dst, name)
        else:
            pass
        
def configurePort(port):
    print(port)
    
def configureHost(host):
    print(host)
    
def configureAddress(address, dst, name):
    print("configureAddress: ", address) 
    file_path = dst  + "/" + name + "/iocBoot/iocgpib/st.cmd"
    changePermission(file_path)
    content_search = "ADDR="
    new_line = 'dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=%s"\n' % str(address)
    changeContent(file_path, content_search, new_line)
    
def configurePV(pvname, dst, name):
    print("pvname input: ", pvname)
    print("configurePV: ", pvname) 
    file2 = dst + "/" + name + "/iocBoot/iocgpib/envPaths"
    changePermission(file2)
    line2 = 'epicsEnvSet("IOC",%s)\n' % pvname
    content2 = "IOC"
    changeContent(file2, content2, line2)

    file3 = dst + "/" + name + "/iocBoot/iocgpib/envPaths"
    top_path = dst  + "/" + name + "/"
    changePermission(file3)
    line3 = 'epicsEnvSet("TOP", %s)\n' % top_path
    content3 = "TOP"
    changeContent(file3, content3, line3)
        
def runApp(dst, name):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./st.cmd"
    path = dst  + "/" + name + "/iocBoot/iocgpib"
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


@app.route('/selected',methods=['GET' ,'POST'])
def selected():
    device=request.form['username']
    return jsonify(username=username)
       
@app.route('/ajax', methods = ['POST'])
def openioc():
    i = IOCS()
    print(request.form)
    name = request.form['name']
    operation= request.form['operation']
    shouldbeopendIOC_list = []
    shouldbeopendIOC_list.append(name)
    if operation =="Stop":
        status = "stopped"
        i.closeObj(name)
        status = "stopped"
        deleteName(name, "/home/pi/shouldbeopenedIOC.txt")
    elif operation =="Start":        
        i.openObj(name)
        status = "running"
        saveFile(name, "/home/pi/shouldbeopenedIOC.txt")
    return jsonify(name=name, status=status)


def changeJSONFile(name, status, file):
    i = IOCS()
    with open(file, 'w') as f:
        data = i.getObj_parameters(str(name), TEMPLATE_PATH)
        #print("content is ", json_data)
        data['status'] = status
        json.dump(data, f)
        
def saveFile(name, file):
    shutil.chown(file, user="pi", group="pi")
    os.chmod(file, stat.S_IRUSR+stat.S_IWUSR+stat.S_IXUSR+stat.S_IRGRP+stat.S_IWGRP+stat.S_IXGRP)
    f = open(file, 'r')
    data = f.read()
    if name in data:
        print("ok")
    else:
        f = open(file, 'a')
        f.write(name + "\n")
    #f.close()
def deleteName(name, file):
    shutil.chown(file, user="pi", group="pi")
    os.chmod(file, stat.S_IRUSR+stat.S_IWUSR+stat.S_IXUSR+stat.S_IRGRP+stat.S_IWGRP+stat.S_IXGRP)
    with open(file, 'r') as f:
        lines = f.readlines()
      
    with open(file, 'w') as f:
        for line in lines:
            print(line)
            if line.strip('\n') != name:
                print("NOOOOOOOO")
                f.write(line)
            else:
                pass
    #f.close()
  
@app.route('/template', methods = ['GET','POST'])
def template():
    i = IOCS()
    print(request.form)
    name = request.form['template']   
    return jsonify(name=name)

@app.route('/closeioc', methods = ['POST'])
def closeioc():
    i = IOCS()
    username = request.form['username']
    iocname = request.form['iocname']
    i.closeObj(username)
    return jsonify(username=username, iocname=iocname)

@app.route('/optionsALL', methods=['GET','POST'])
def optionsALL():
    i = IOCS()
    options_list= i.getConfiguredIOC()
    return jsonify({'options':options_list})

@app.route('/result', methods=['GET', 'POST'])
def result():
    dst = DST
    name = request.form['dev']
    if request.method == 'POST':
      
        if 'action' in request.form:
            if request.form['action'] == 'startIOC':
                result= "ok"
                try:
                    
                    runApp(dst, name)
                except:
                    render_template('error.html')
            elif request.form['action'] == 'stopIOC':
                result= "stop"
                try:
                    closeApp(dst)
                except:
                    render_template('error.html')
            elif request.form['action'] == 'home':
                return "add new IOC ok"
            elif request.form['action'] == 'cancel':
                return "cancel"
            else:
                return("No action executed")
        else:
                return("NO action form")
    
    return render_template('result.html', devices=devices_dict, result=result, reload_content=reload_content)

def runApp(dst, name):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./external_start"
    path = dst  + "/" + name + "/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout
    #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd=path)
    #with process.stdout:
           #log_subprocess_output(process.stdout)
    #exitcode = process.wait() # 0 means success
    
def closeApp(dst, name):
    print("start IOC")
    logging.info('runApp: openKeithley2000IOC. {}'.format(time.asctime(time.localtime(time.time()))))
    command_line_args = "./external_stop"
    path = dst  + "/" + name + "/iocBoot/iocgpib"
    process = subprocess.run(command_line_args, shell=True, cwd=path)
    output = process.stdout

@app.route('/tp/<name>', methods=['GET','POST'])
def getTemplateParameters(name):
    IOCS = IOCS()
    parameters_dict= IOCS.getObj_parameters(name, "/home/pi/Templates/Keithley/keithley2000")
    i = 0
    list_html = []
    table ="""<table style="border-collapse:seperate; border-spacing: 4em 4em;">"""
    if parameters_dict:
        parameters_number = len(parameters_dict)
        print(parameters_number)
        for parameter in parameters_dict:
            list_html.append(parameter)
       
            list_html.append(parameters_dict[parameter])
            parameter_line = """<tr>
<td><b>%s</b>
</td>
<td id="%s" name="%s" >%s</td> 
</tr>""" % (parameter,parameter, parameter, parameters_dict[parameter])
            table += parameter_line
        button_html = """
<tr>  
    
<td>
               <button id= "ok" name="ok"> <label>OK</label> </button>       
    </td>
    <td>
               <button id= "canceln" name="canceln"> <label>Canceln</label> </button>       
    </td>     
</tr></table>

""" 
        table +=button_html
        parameter_line = """<tr>
<td><b> %s </b>
</td>
<td> %s
</td>
</tr>"""
        table_html= """
<table>
<tr>
<td><b> %s </b>
</td>
<td> %s
</td>
</tr>

<tr>
<td> <b> %s </b>
</td>
<td> %s
</td>
</tr>
<tr>
<td> <b> %s </b>
</td>
<td> %s
</td>
</tr>
</table>


    """ % (list_html[0], list_html[1],list_html[2],list_html[3],list_html[4], list_html[5])

    return table



    
@app.route('/<name>', methods=['GET','POST'])
def getIOC(name):
    i = IOCS()
    parameters_dict= i.getObj_parameters(name,"/home/pi/ConfiguredIOC" )
    parameters_full_list = i.getObj(name)
    i = 0
    list_html = []
    table ="""<table style="border-collapse:seperate; border-spacing: 4em 4em;">"""
    if parameters_full_list:
        operation = parameters_full_list[0]['operation']
        status = parameters_full_list[0]['status']
        parameters_number = len(parameters_dict)
        print(parameters_number)
        for parameter in parameters_dict:
            if parameter != "status":
                list_html.append(parameter)
       
                list_html.append(parameters_dict[parameter])
            
                parameter_line = """<tr>
<td><b>%s</b>
</td>
<td id="%s" name="%s" >%s</td> 
</tr>""" % (parameter,parameter, parameter, parameters_dict[parameter])
            
                table += parameter_line
            else:
                parameter_line = """<tr>
<td><b>%s</b>
</td>
<td id="%s" name="%s" >%s</td> 
</tr>""" % (parameter,parameter, parameter, status)
                table += parameter_line
                
        button_html = """
<tr>  
     <td>  
               <button onclick="return loadXMLDoc()" id="stop-button" name="stop"> <label id="operation">%s</label></button>     
    </td>
<td>
               <button onclick="return Delete()" id= "delete-button" name="remove"> <label>Remove</label> </button>       
    </td>            
</tr></table>

""" % (operation)
        table +=button_html
        parameter_line = """<tr>
<td><b> %s </b>
</td>
<td> %s
</td>
</tr>"""
        table_html= """
<table>
<tr>
<td><b> %s </b>
</td>
<td> %s
</td>
</tr>

<tr>
<td> <b> %s </b>
</td>
<td> %s
</td>
</tr>
<tr>
<td> <b> %s </b>
</td>
<td> %s
</td>
</tr>
</table>


    """ % (list_html[0], list_html[1],list_html[2],list_html[3],list_html[4], list_html[5])

    return table


@app.route('/addnew/<name>', methods=['GET','POST'])
def addnewioc(name):
    IOC = IOCS()
    options_list= IOC.getTemplates()
    print(options_list)
    name_list= []
    for i in options_list:
        print(i['description'])
        name_list.append(i['description'])
    if name in name_list:
        button = """
                <input type="hidden" name="templateChosen" id="templateChosen" value="%s">
               <button type="submit" id="add" name="action" value="add"> Add</button> """ % name
    else:
        button = """<input type="hidden" id="templateChosen" value="%s">""" % name
    print(button)
    return button

@app.route('/templates')
def getTemplatesALL():
    i = IOCS()
    options_list= i.getTemplates()
    return jsonify({'options':options_list})

@app.route('/remove', methods=['POST'])
def remove():
    i = IOCS()
    print(request.form)
    name = request.form['name']
    i.closeObj(name)
    i.removeObj(name)
    return jsonify(name=name)


                    
if __name__ == "__main__":
    app.run(host='192.168.1.101', port='8080', threaded=True)
