# Aim
Writing a Epics Server to connect GPIB Devices on Raspberry PI Platform 

# Raspberry Pi
Raspberry Pi is a small functional linux computer. We would like to use it for the extra implementation for the experiment control due to its small size and functional property. On the Raspberry Pi we can get the GPIB Interface for the devices. Now our aim is to write Epics Server for GPIB Device Control on Raspberry Pi.


# Epics Server 

https://epics.anl.gov/modules/bus/gpib/gpibCore/R1-1/gpib.html

## Epics Base 

## Epics Support 

### To do: 

   Read Epics Streamdevice and Asyn documentation and find how they work. 
   
   https://www.esrf.eu/files/live/sites/www/files/events/conferences/2011/ESRFUP-WP10-beamline-instrumentation-software/WP10-DIAMOND-AsynDriverEPICS.pdf
   
   https://www.slac.stanford.edu/grp/ssrl/spear/epics/site/asyn/devGpib.html
   
   https://paulscherrerinstitute.github.io/StreamDevice/
   
# GPIB Device support
1. Test how GPIB works. It works with Keithley 2000. When I use Python to test the GPIB function, sending commands and getting the answers are OK. The old patch version of linux-gpib-4.1.0 for raspi-gpib_driver is no longer there. So I decide to install the newest 4.3.0 Version. 

Information link:
https://sourceforge.net/projects/linux-gpib/files/
https://github.com/elektronomikon/raspi_gpib_driver

      Install linux-gpib and raspi_gpib_driver. Complete code can be seen in the link. Version 4.2.0 is installed. The source code is unten ~/Downloads/HHL/

      
       >>> cd ~/Downloads
       >>> mkdir HHL
       >>> git clone https://github.com/elektronomikon/raspi_gpib_driver.git


       >>> tar xzf linux-gpib-kernel-4.2.0.tar.gz
       >>> cd linux-gpib-kernel-4.2.0
       >>> ./configure
       -----patch-----
       >>> make 
       >>> sudo make install
       
2. After installing linux-gpib and raspi patch packages. we can use ibtest and ibterm to test the gpib. 19 is the address of the GPIB device. 
       
       >>> ibterm -b 19 -N
       (Enter 2 times)
       
       
3. python 3 test:
       >>> from gpib_ctypes import gpib
       >>> device = gpib.dev(0,19)
       >>> gpib.write(device, b’*IDN?’)
       >>> gpib.read(device, 100)
      
# Connection 
in Configure file:

change LINUX_GPIB=0 as LINUX_GPIB=YES

Add command: GpibBoardDriverConfig(PortName, autoconnect, BoardIndex, timeout, priority) 

