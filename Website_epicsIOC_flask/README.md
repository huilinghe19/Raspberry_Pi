# Webserver on Raspberry Pi (GPIB and EPICS SERVER INSTALLED)
In oder to give more possibility to use more device servers, flask web server comes into our sight. After opening a website, the devices informations can be changed and configured. In the end, the device IOC can be started with a button directly. It is very simple for those who are no familiar with the instruments. 


# Method with flask

flask is already in Raspberry Pi. Super!

In other systems, install flask with "apt install python3-flask python3-flask-api" or  "pip install --upgrade Flask"

## website with HTML

I habe used just one index.html file under "Webserver/templates". This html comes from jördis index.html originally. But I have deleted all other irrelevant things except a button and a block to show some sentences. css js bootstrap (such things of format) are also not included. In the future I will add somethings to complete the whole functions. 

## flask script
In flask_server.py, the original index link / is still there. The index page shows the informations about how we can get the IOC with links. The button in the index page has no effect.  Other links like /openKeithley2000IOC are used to open IOC.

## open webserver with PYTHON scripts

>>> python3 flask_server.py

There are 3 websites: (ip address of raspberry pi is: 192.168.1.101) 

http://192.168.1.101:8080

http://192.168.1.101:8080/openKeithley2000IOC

http://192.168.1.101:8080/openKeithley3000IOC (just for testing, has the same function with Keithley 2000)


## Button on the websites: there is a button "start IOC" 

http://192.168.1.101:8080/openKeithley2000IOC 

we can press the button :"start IOC", then EPICS IOC for keithley 2000 is open. We can use "camonitor iocgpib:value" to get the voltage value.

