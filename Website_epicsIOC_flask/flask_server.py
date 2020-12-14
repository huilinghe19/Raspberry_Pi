from flask import Flask, request, render_template
import binascii #needed for encoding, decoding hex to ascii/ ascii to hex
#import GPIB_Server_Functions as ServerGPIB 

import os
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging


app = Flask(__name__)

logging.basicConfig(filename="myapp.log", level=logging.INFO)

devices_dict = {}
reload_content = {}
result = ''

@app.route('/', methods=['GET' ,'POST'])
def open_index():
    global devices_dict;global reload_content;global result
    if request.method == 'POST' :
        if 'action' in request.form:
            reload_content = request.form.to_dict() #cast to dict so values can be changed; request.form elements are immutable
            handle = devices_dict[request.form['active_element']]['handle'] #get handle int from selected device
            command = request.form['command']
            bytes_to_read = request.form['bytes_to_read']
            if request.form['action'] == 'send only':
                if request.form['send_coding'] == 'hexadecimal':
                    command = bytes.fromhex(command).decode('ascii')
                #ServerGPIB.send_only(command,handle)
            elif request.form['action'] == 'read only':
                #result = ServerGPIB.read_only(handle, bytes_to_read)
                if request.form['read_coding'] == 'hexadecimal':
                    result = result.encoding('ascii')
                    result = binascii.hexlify(result)
            elif request.form['action'] == 'send and read':
                if request.form['send_coding'] == 'hexadecimal':
                    command = bytes.fromhex(command).decode('ascii')
                #result = ServerGPIB.send_and_read(command, handle, bytes_to_read)
                if request.form['read_coding'] == 'hexadecimal':
                    result = result.encode('ascii')
                    result = binascii.hexlify(result)
                    result = result.decode('ascii')
            else:
                print("ERROR: bad 'action' value")
            #reload_content['status_byte'] = ServerGPIB.get_ibsta()
            #reload_content['ibsta'] = ServerGPIB.get_ibsta()
            #reload_content['result'] = reload_content['result'].replace('\r\n','')

        else:
            #devices_dict = ServerGPIB.get_available_devices()
            result = ''
            print(reload_content)
    print(reload_content)
    return render_template('index.html',devices=devices_dict, result=result, reload_content=reload_content)



@app.route('/openKeithley2000IOC', methods=['GET' ,'POST'])
def open_keithley2000ioc():
    if request.method == 'POST' :
        runApp()
        logging.info('open_keithley2000ioc Started. {}'.format(time.asctime(time.localtime(time.time()))))
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content)
def runApp():
        command_line_args = "./st.cmd"
        process = subprocess.run(command_line_args, shell=True, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
        output=process.stdout
        logging.info('runApp: Keithley 2000 IOC is Started. {}'.format(time.asctime(time.localtime(time.time()))))
        #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
        #with process.stdout:
        #       log_subprocess_output(process.stdout)
        #exitcode = process.wait() # 0 means success

@app.route('/openKeithley3000IOC', methods=['GET' ,'POST'])
def open_keithley3000ioc():
    if request.method == 'POST' :
            runApp()
            logging.info('open_keithley3000ioc Started. {}'.format(time.asctime(time.localtime(time.time()))))
    return render_template('index.html', devices=devices_dict, result=result, reload_content=reload_content)

def runApp():
        command_line_args = "./st.cmd"
        process = subprocess.run(command_line_args, shell=True, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
        output=process.stdout
        #process = Popen(command_line_args, stdout=PIPE, stderr=STDOUT, cwd="/home/pi/gpib_test/iocBoot/iocgpib")
        #with process.stdout:
        #       log_subprocess_output(process.stdout)
	#exitcode = process.wait()



if __name__ == "__main__":    
    #app.run(host='134.30.36.95', port='8080', threaded=True)
    app.run(host='192.168.1.101', port='8080', threaded=True)
