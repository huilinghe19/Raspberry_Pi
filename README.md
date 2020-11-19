# Aim
Writing a Epics Server to connect GPIB Devices on Raspberry Platform 

# Raspberry_Pi
Raspberry Pi is a small functional linux computer. We would like to use it for the extra implementation for the experiment control due to its small size and functional property. On the Raspberry Pi we can get the GPIB Interface for the devices(to be proved!!!). Now our aim is to connect the Raspberry Pi with Epics IOC for GPIB Device Control.


# Epics Server 
1. Epics Base works on Raspberry Pi. (using Jördis Dokumentation).
   To do: Read Epics Streamdevice and Asyn documentation and find how they work. 
   
# GPIB Device support
1. Test how GPIB works. It does not work. No package gpib_ctypes is installed. 
      Install linux-gpib and raspi_gpib_driver. Information link: https://github.com/elektronomikon/raspi_gpib_driver

      
       cd ~/Downloads
       mkdir HHL
       git clone https://github.com/elektronomikon/raspi_gpib_driver.git


       tar xzf linux-gpib-kernel-4.2.0.tar.gz
       cd linux-gpib-kernel-4.2.0
       ./configure
       
2. After installing linux-gpib and raspi patch packages. There is something wrong in GPIB configuration file. 
       
       >>> ibterm -b19
       >>> Error
       >>> sudo nano gpib.config
       >>> ??????
            
