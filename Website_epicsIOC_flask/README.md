# Webserver on Raspberry Pi (GPIB and EPICS SERVER INSTALLED)
In oder to give more possibilities to use device servers, flask web server comes into our sight. After opening a website, the devices informations can be changed and configured. In the end, the device IOC can be started with a button directly. It is very simple for those who are not familiar with the device IOCs. 


# Method with flask

flask and related packages are already in Raspberry Pi. Super!

In other systems, install flask with "apt install python3-flask python3-flask-api" or  "pip install --upgrade Flask". Maybe something else should be installed to satisfy your needs.

## website with HTML

I habe used an index.html file under "Webserver/templates". This html comes from jördis index.html originally. But I have deleted all other irrelevant things except a button and a block to show some sentences. css js bootstrap (such things of format) are also not included. In the future I will add somethings to complete the whole functions. 

## flask script
In flask_server.py, The index page shows the informations about how we can get the IOC with address. 

## open webserver with PYTHON scripts

>>> python3 flask_server.py

There are 2 websites: (ip address of raspberry pi is: 192.168.1.101) 

http://192.168.1.101:8080

http://192.168.1.101:8080/openKeithley2000IOC


## Button on the websites: there is a button "Start IOC" 
after choosing the address 19 and writing the pv name, press the button :"Start IOC", then EPICS IOC for keithley 2000 is open. We can use "camonitor {pvname}:value" to get the voltage value. Other addresses do not work. The error messages with other addresses will be shown after starting the python scripts in terminal, just like epics ioc error messages


