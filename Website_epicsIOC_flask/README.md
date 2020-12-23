# Webserver on Raspberry Pi (GPIB and EPICS SERVER INSTALLED)
In oder to give more possibilities to use device servers, flask web server comes into our sight. After opening a website, the devices informations can be changed and configured. In the end, the device IOC can be started with a button directly. It is very simple for those who are not familiar with the device IOCs.

# Current work
try to use flask with docker to deploy the small project( to start epics IOC with GPIB address and pv name). JUST TRY DOCKER USAGE.
## Gunicorn + Gevent     
    sudo apt install gunicorn3
    sudo apt install python3-gevent
    gunicorn3 flask_server:app -c gunicorn.conf.py
    
# Usage
## INSTALL flask 
flask and related packages are already in Raspberry Pi. Super! In other systems, install flask with "apt install python3-flask python3-flask-api" or  "pip install --upgrade Flask". Maybe something else should be installed to satisfy your needs.

## Download the whole repository
    git clone https://github.com/huilinghe19/Raspberry_Pi.git
    cd Raspberry_Pi
    
## Open the website: 
    >>> sudo python3 flask_server.py

There are 2 websites: (ip address of raspberry pi is: 192.168.1.101) 

http://192.168.1.101:8080

http://192.168.1.101:8080/configure


  The ip address of the raspberry pi which I use is: 192.168.1.101. if the host is different, then you can change the address in the "flask_server.py". Of course, you can also use following commands to open the flask server.
   
    export FLASK_APP=flask_server
    flask run --host=0.0.0.0


## website with HTML

 all html pages should be put under /templates. It has such a stucture.


## Button on the websites: "Start IOC" 
after choosing the address 19 and writing the pvname, press the button :"Start IOC", then EPICS IOC for keithley 2000 is open. We can use "camonitor {pvname}:value" to get the voltage value. Other addresses do not work. The error messages with other addresses will be shown after starting the python scripts in terminal, just like epics ioc error messages


