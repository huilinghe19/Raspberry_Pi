# Epics Server for GPIB Devices on Raspberry Pi

## Aim
Writing a Epics IOC to connect GPIB Devices (Example:keithley 2000 multimeter) on Raspberry PI Platform 

## Progress
Have installed gpib server and epics server.  have wrote a epics IOC "gpib_test" for Keithley 2000, have got the voltage value of keithley 2000. Have wrote a webserver to open Keithley 2000 epics IOC. 

# Raspberry Pi
Raspberry Pi is a small functional linux computer. We would like to use it for the extra implementation for the experiment control due to its small size and functional property. On the Raspberry Pi we can get the GPIB Interface for the devices. Our aim is to write Epics Server for GPIB Device Control on Raspberry Pi. We have installed the newest raw version 5.4 Raspi(2020-08-20-raspios-buster-armhf-full.img). 

All imgs are stored under "~/raspi_image" on dide17 for Backup.
   
# GPIB Device support

## Test how GPIB works. It works with Keithley 2000. (with python3, install gpib_ctypes) 
    

       >>> from gpib_ctypes import gpib
       >>> device = gpib.dev(0,19)
       >>> gpib.write(device, b’*IDN?’)
       >>> gpib.read(device, 100)

When I use Python or python3 (without raspi-gpib installation)to test the GPIB function, sending commands and getting the answers are OK.  
## Install linux-gpib and raspi_gpib_driver.

The old patch version of linux-gpib-4.1.0 for raspi-gpib_driver is no longer there. The other versions do not work well with Raspi Kernel 5.4. After several tries, we decide to install the newest 4.3.3 Version. 

Information link:
https://sourceforge.net/projects/linux-gpib/files/
https://github.com/elektronomikon/raspi_gpib_driver

###  Basic methods are:
      
       >>> cd ~/Downloads
       >>> mkdir HHL
       >>> git clone https://github.com/elektronomikon/raspi_gpib_driver.git


       >>> tar xzf linux-gpib-kernel-4.3.3.tar.gz
       >>> cd linux-gpib-kernel-4.3.3
       >>> ./configure
       -----patch-----
       >>> make 
       >>> sudo make install
       
###  Version 4.3.3 is installed with the following method from Lutz. Now this version is on the Raspi.

#### Put the sources in dide17, mount it on raspberry pi and compile it. It saves the space of Raspi. 

      >>> sudo mount -t nfs 192.168.1.2:hzb /mnt
      >>> cd /mnt/raspberry/linux-gpib-4.3.3/linux-gpib-kernel-4.3.3
      >>> make clean (in kernel linux-gpib-kernel-4.3.3, patch is already done in the source)
      >>> make GPIB_DEBUG=1 VERBOSE=1 V=1
      >>> make install
      (do it again in linux-gpib-user-4.3.3)
      
#### After installing linux-gpib and raspi patch packages. we can use ibtest and ibterm to test the gpib. 19 is the address of the GPIB device. 

       >>> sudo modprobe gpib_common
       >>>sudo modprobe raspi_gpib
       >>> sudo ldconfig
       >>> sudo gpib_config 
       >>> ibterm -b 19 -N
       (Enter 2 times)
       keithley .......

     
# Epics Server 

https://epics.anl.gov/modules/bus/gpib/gpibCore/R1-1/gpib.html

## Epics Base

base <https://epics-controls.org/resources-and-support/base/>
## Epics Support 

### asyn 

<https://github.com/epics-modules/asyn>

### StreamDevice 

https://github.com/paulscherrerinstitute/StreamDevice

### Extra Informations

   https://www.esrf.eu/files/live/sites/www/files/events/conferences/2011/ESRFUP-WP10-beamline-instrumentation-software/WP10-DIAMOND-AsynDriverEPICS.pdf
   
   https://www.slac.stanford.edu/grp/ssrl/spear/epics/site/asyn/devGpib.html
https://github.com/paulscherrerinstitute/StreamDevice
      
## Connection 

https://epics-controls.org/resources-and-support/documents/howto-documents/gpib-ports-linux-streamdevice/#STEP_3_Create_a_protocol_file

Changes in bashrc file: 
https://prjemian.github.io/epicspi/


### Change in Configure file:
#### change LINUX_GPIB=NO as LINUX_GPIB=YES
#### Add command in st.cmd file: GpibBoardDriverConfig(PortName, autoconnect, BoardIndex, timeout, priority) 
The boardindex must the same as the Interface board index in the gpib.conf file.
#### Board name "raspi_gpio_interface" in file "gpib.conf" is not allowed to be changed, in oder to be connected with the epics IOC.
