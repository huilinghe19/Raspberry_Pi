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
from wtforms import Form
import IOC
from IOC import IOCS

#SECRET_KEY = 'development'
app = Flask(__name__)
logging.basicConfig(filename="myapp.log", level=logging.INFO)

### Old definition, may be used in future
devices_dict = {}
reload_content = {}
result = ''
###
SRC = "/home/pi/Templates/Keithley/keithley2000"
DST = "/home/pi/ConfiguredIOC"

UPLOAD_DIRECTORY = DST

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


#DST= "/home/pi/configuredIOC"
address_list = [{'address':'19'}, {'address':'1'},{'address':'2'}, {'address':'3'}, {'address':'4'}, {'address':'5'}, 
{'address':'6'}, {'address':'7'},  {'address':'8'}, {'address':'9'}, {'address':'10'}, {'address':'11'},  {'address':'12'}, {'address':'13'}, {'address':'14'},
 {'address':'15'},  {'address':'16'}, {'address':'17'}, {'address':'18'}, {'address':'20'}, {'address':'21'}, {'address':'22'},
 {'address':'23'},  {'address':'24'}, {'address':'25'}, {'address':'26'}, {'address':'27'},  {'address':'28'}, {'address':'29'}, {'address':'30'}, {'address':'31'}]

        
@app.route('/',methods=['GET' ,'POST'])
def index():
    i = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]
    #parameters= i.getObjParameters_list("test")
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())


@app.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@app.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


@app.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""

    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)

    # Return 201 CREATED
    return "", 201


@app.route('/selected',methods=['GET' ,'POST'])
def selected():
    device=request.form['username']
    return jsonify(username=username)

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
    
        
@app.route('/ajax', methods = ['POST'])
def openioc():
    i = IOCS()
    username = request.form['username']
    iocname = request.form['iocname']
    mark = "*"
    if mark in iocname:
        i.closeObj(username)
    else:
        i.openObj(username)
    return jsonify(username=username, iocname=iocname)

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

@app.route('/parameters', methods = ['POST'])
def parameters():
    i = IOCS()
    
    return jsonify({"test":i.getObjParameters("test", "/home/pi/ConfiguredIOC")})
    
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
    

    
@app.route('/<name>', methods=['GET','POST'])
def getIOC(name):
    i = IOCS()
    #name_list= i.getObj(name)
    #for item in name_list:
        #result = item
    #return jsonify(result)
   
    parameters_dict= i.getObj_parameters(name)
    parameters_full_list = i.getObj(name)
    operation = parameters_full_list[0]['operation']
   
    
    parameters_number = len(parameters_dict)
    i = 0
    list_html = []
    table ="""<table>"""
    for parameter in parameters_dict:
        list_html.append(parameter)
       
        list_html.append(parameters_dict[parameter])
        parameter_line = """<tr>
<td><b> %s </b>
</td>
<td> %s
</td> 
</tr>""" % (parameter,parameters_dict[parameter])
        table += parameter_line
    button_html = """
<tr>
  
     <td>  
               <button onclick="return loadXMLDoc()" id= "stop-button" name="stop"> <label id="stop">%s</label>       </button>      <div id="myDiv"></div>    
    </td>
<td>  
               <button onclick="return loadXMLDocRemove()" id= "remove" name="remove"> <label>Remove</label>      </button>       <div id="myDiv22"></div>  
    </td>

  
  
     

                         

            
</tr></table>

""" % operation
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
   

@app.route('/templates')
def getTemplatesALL():
    i = IOCS()
    options_list= i.getTemplates()
    return jsonify({'options':options_list})

@app.route('/templates/<string:name>', methods=['GET','POST'])
def getTemplate(name):
    i = IOCS()
    name= i.getTemplateObj(name)
    for item in name:
        result = item
    return jsonify(result)

@app.route('/remove', methods=['GET','POST','DELETE'])
def remove():
    i = IOCS()
    username = request.form['username']
    i.removeObj(username)
@app.route('/new', methods = ['POST'])
def oc():
    i = IOCS()
    username = request.form['username']

    return jsonify(username=username)
    #return redirect(url_for("add"), username=username)
    

@app.route('/add', methods=['GET', 'POST'])
def add():
    i = IOCS()
    headers = [' ', 'IOC']
    headers_templates = [' ','Templates' ]

    template = request.form['templates_list']
    print("choose template : ", template)
    if request.method == 'POST':
        print(request.form)
        template = request.form['templates_list']
        print("Template : ", template)
        print(request.form)
        if 'action' in request.form:
            if request.form['action'] == 'add':
                try:
                    print("ok")
                    return render_template('addnewioc.html',devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())
                   
                except:
                    render_template('error.html')
            else:
                return("NO action: add")
        else:
            return("NO action")
    #return render_template('addnewioc.html',devices=devices_dict, result=result, reload_content=reload_content, data=address_list,
                           #headers = headers, objects = i.getConfiguredIOC(), headers_templates = headers_templates, objects_templates = i.getTemplates())

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
