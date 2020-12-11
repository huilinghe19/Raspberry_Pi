#!../../bin/linux-arm/gpib

## You may have to change gpib to something else
## everywhere it appears in this file

< envPaths
epicsEnvSet(STREAM_PROTOCOL_PATH, "../../gpibApp/Db")
cd "${TOP}"

## Register all support components
dbLoadDatabase("dbd/gpib.dbd")
gpib_registerRecordDeviceDriver(pdbbase)

epicsEnvSet("Port", "raspi_gpio_interface")

GpibBoardDriverConfig("$(Port)", "1", "0", "3", "0")
## Load record instances
#dbLoadTemplate "db/Keithley2000.substitutions"
dbLoadRecords "db/yourdev.db", "P=${IOC}:,PORT=$(Port),ADDR=19"

#dbLoadRecords "db/dbExample1.db", "P=${IOC}:,PORT=$(Port),ADDR=19"
#dbLoadRecords "db/keithleyHHL.db", "user=pi, P=${IOC}:,PORT=$(Port),ADDR=19"
#dbLoadRecords "db/dbSubExample.db", "P=${IOC}:,PORT=$(Port),ADDR=19"

#dbLoadRecords "db/user.substitutions"

## Set this to see messages from mySub
#var mySubDebug 1

## Run this to trace the stages of iocInit



#traceIocInit

cd "${TOP}/iocBoot/${IOC}"
iocInit()

## Start any sequence programs
#seq sncExample, "user=root"
