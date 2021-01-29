import os, sys, stat
import time
import shutil
import requests
from pathlib import Path
from flask import Flask, request, render_template, jsonify, make_response, render_template_string
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
    i = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    #parameters= i.getObjParameters_list("test")
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())

@app.route('/add', methods=['GET', 'POST'])
def add():
    i = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    print("choose template : ", request.form['templateChosen'])
    chosenTemplate=request.form['templateChosen']
    data = getConfigureFile(TEMPLATE_PATH + chosenTemplate + "/" + "parameters.json")
    print(data.keys())
    parameters_list = []
    address = data['address']
    newdev= data['name']
    pvname= data['pvname']
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
                        print(data[i])
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
            <select name="comp_select" class="selectpicker form-control">
              {% for o in data %}
              <option value="{{ o.address }}">{{ o.address }}</option>
              {% endfor %}
            </select>
    </div>
</div>
<button type="submit" onclick="start_loading_animation(this) class="btn btn-default" name="action" value="getAddress">OK</button>
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
                    #return render_template('addnewioc.html',devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           #headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())
                   
                except:
                    render_template('error.html')
            else:
                return("NO action: add")
        else:
            return("NO action")
    return render_template('addnewioc.html',devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())
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

    
### Configure the address and pv name
@app.route('/configure', methods=['GET', 'POST'])
def configure():
    newdev = request.form['newdev']
    pvname_input = request.form['pv_name']
    address_input = request.form.get('comp_select')
    templateChosen= request.form['templateChosen']
    print("choose template : ", request.form['templateChosen'])
    
    if pvname_input and newdev:
        print("pvname: ", pvname_input)
        print("Device name: ", newdev)  
        if request.method == 'POST':
            print(request.form)
            if 'action' in request.form:
                if request.form['action'] == 'getAddress':
                    try:
                        logging.info('get address {}, pv name {}, {}'.format(address_input, pvname_input, time.asctime(time.localtime(time.time()))))
                        print("get Address {}".format(address_input))
                        dst = DST
                        src = TEMPLATE_PATH + "/" + templateChosen
                        configure_parameters = {"address": str(address_input), "pvname": str(pvname_input)}
                        copyTemplates(src, dst+ '/'+ newdev)
                        print("copyTemplates")
                        configure(configure_parameters, dst, newdev)
                        dict_parameters = {"name": newdev, "pvname": pvname_input, "address":address_input}
                        parameters = dict(device=dict_parameters)
                        configureFile(parameters, dst+ '/'+ newdev +'/'+ "parameters.json" )
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

    return render_template('keithley2000.html', data=str(address_input), name=str(pvname_input), dev = str(newdev), devices=devices_dict, result=result, reload_content=reload_content)
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
    if operation =="Stop":
        i.closeObj(name)
    elif operation =="Start":
        i.openObj(name)
        
    return jsonify(name=name)
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
    
    return render_template('result.html', devices=devices_dict, result=result, reload_content=reload_content )
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

    
@app.route('/<name>', methods=['GET','POST'])
def getIOC(name):
    i = IOCS()
    parameters_dict= i.getObj_parameters(name)
    parameters_full_list = i.getObj(name)
    if parameters_full_list:
        operation = parameters_full_list[0]['operation']
        parameters_number = len(parameters_dict)
    else:
        pass
    i = 0
    list_html = []
    table ="""<table style="border-collapse:seperate; border-spacing: 4em 4em;">"""
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
               <button onclick="return loadXMLDoc()" id="stop-button" name="stop"> <label id="operation">%s</label></button>     
    </td>
<td>
               <button onclick="return Delete()" id= "delete-button" name="remove"> <label>Remove</label> </button>       
    </td>            
</tr></table>

""" % (operation)
    table +=button_html
    print(list_html)
    print(table)
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
    i = IOCS()
    options_list= i.getTemplates()
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
    i.removeObj(name)
    return jsonify(name=name)


                    
if __name__ == "__main__":
    app.run(host='192.168.1.101', port='8080', threaded=True)
