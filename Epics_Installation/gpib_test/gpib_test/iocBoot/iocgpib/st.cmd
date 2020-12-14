#!../../bin/linux-arm/gpib

## You may have to change gpib to something else
## everywhere it appears in this file

< envPaths
epicsEnvSet(STREAM_PROTOCOL_PATH, "../../gpibApp/Db")
cd "${TOP}"

## 1  Register all support components
dbLoadDatabase("dbd/gpib.dbd")
gpib_registerRecordDeviceDriver(pdbbase)


## 2 Configure your asynPorts
# 2a GPIB: portname, autoConnect, boardId, timeout, 5th_arg
     # Note1: The portname has to match the interface name of your board
     #        from /etc/gpib.conf!
     # Note2: boardId is the GPIB address *of your GPIB controller board*.
     #        The GPIB address of the _device_ itself is supplied to
     #        dbLoadRecords under step 3 below.

epicsEnvSet("Port", "raspi_gpio_interface")

GpibBoardDriverConfig("$(Port)", "1", "0", "3", "0")


# 2b TCP/IP socket: IPaddress:port
#drvAsynIPPortConfigure("IPPORT","192.168.0.1:6789")

# 2c Serial: "COM1", 9600 bps, 8N1, flow contr.: XON/XOFF
#drvAsynSerialPortConfigure ("SERIALPORT", "/dev/ttyS0", 0, 0, 0)
#asynSetOption ("SERIALPORT", 0, "baud", "9600")
#asynSetOption ("SERIALPORT", 0, "bits", "8")
#asynSetOption ("SERIALPORT", 0, "parity", "none")
#asynSetOption ("SERIALPORT", 0, "stop", "1")
#asynSetOption ("SERIALPORT", 0, "clocal", "Y")
#asynSetOption ("SERIALPORT", 0, "crtscts", "N")

# 2d vxi11: ...


## 3 Load record instances
# Make sure you have your device's GPIB address right!
#dbLoadTemplate "db/Keithley6485.substitutions"
dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=19"

## Set this to see messages from mySub
#var mySubDebug 1

## Run this to trace the stages of iocInit



#traceIocInit

cd "${TOP}/iocBoot/${IOC}"
iocInit()

## Start any sequence programs
#seq sncExample, "user=root"
