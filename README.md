# Aim
Writing a Epics Server to connect GPIB Devices on Raspberry PI Platform 

# Raspberry_Pi
Raspberry Pi is a small functional linux computer. We would like to use it for the extra implementation for the experiment control due to its small size and functional property. On the Raspberry Pi we can get the GPIB Interface for the devices. Now our aim is to write Epics Server for GPIB Device Control on Raspberry Pi.


# Epics Server 
1. Epics Base works on Raspberry Pi.

2. To do: 

   Read Epics Streamdevice and Asyn documentation and find how they work. 
   
   https://www.esrf.eu/files/live/sites/www/files/events/conferences/2011/ESRFUP-WP10-beamline-instrumentation-software/WP10-DIAMOND-AsynDriverEPICS.pdf
   
   https://www.slac.stanford.edu/grp/ssrl/spear/epics/site/asyn/devGpib.html
   
   https://paulscherrerinstitute.github.io/StreamDevice/
   
# GPIB Device support
1. Test how GPIB works. It does not work with Keithley 2000. When I use Python to test the GPIB function, "No package gpib_ctypes is installed. ". The old patch version of linux-gpib-4.1.0 for raspi-gpib_driver is no longer there. So I decide to install the 4.2.0 Version. Information link: https://github.com/elektronomikon/raspi_gpib_driver

      Install linux-gpib and raspi_gpib_driver. Complete code can be seen in the link. Version 4.2.0 is installed. The source code is unten ~/Downloads/HHL/

      
       >>> cd ~/Downloads
       >>> mkdir HHL
       >>> git clone https://github.com/elektronomikon/raspi_gpib_driver.git


       >>> tar xzf linux-gpib-kernel-4.2.0.tar.gz
       >>> cd linux-gpib-kernel-4.2.0
       >>> ./configure
       
2. After installing linux-gpib and raspi patch packages(make install has been done). There is something wrong in GPIB configuration file. GPIB has not been configured in Raspberry. 19 is the address of the GPIB device. 
       
       >>> ibterm -b19
       >>> Error
       >>> sudo nano gpib.config
       >>> ??????
            
# Connection 
in Configure file:

change LINUX_GPIB=0 as LINUX_GPIB=YES

Add command: GpibBoardDriverConfig(PortName, autoconnect, BoardIndex, timeout, priority) 

$ sudo modprobe gpib_common

$ sudo modprobe gpib_bitbang

$ sudo gpib_config

./gpib_config

ibterm -d19
