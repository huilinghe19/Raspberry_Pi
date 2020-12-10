# Webserver on Raspberry Pi (GPIB and EPICS SERVER INSTALLED)
I habe used just a index.html file. The original html comes from jördis index.html. But I have deleted all other things except a button and a block to show some sentences. css js bootstrap things of format are also not included.

In flask_server.py, the original link / is still there. The button has no effect.  I have added another link /openKeithley2000IOC to show how to open IOC.  

## open webserver with PYTHON scripts

>>> python3 flask_server.py

There are 3 websites:

http://192.168.1.101:8080

http://192.168.1.101:8080/openKeithley2000IOC

http://192.168.1.101:8080/openKeithley3000IOC (just for testing, has the same function with Keithley 2000)


## on the websites: there is a button "start IOC"

http://192.168.1.101:8080/openKeithley2000IOC 

we can press the button :"start IOC", then EPICS IOC for keithley 2000 is open. 

