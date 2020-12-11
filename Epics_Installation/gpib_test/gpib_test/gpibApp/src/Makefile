TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS BELOW HERE

# xxxRecord.h will be created from xxxRecord.dbd
DBDINC += xxxRecord

# Install xxxSupport.dbd into <top>/dbd
DBD += xxxSupport.dbd

# I have added the following (Huiling)
DBD += keithley.dbd

# Build an IOC support library
LIBRARY_IOC += gpibSupport

# Compile and add the code to the support library
gpibSupport_SRCS += xxxRecord.c
gpibSupport_SRCS += devXxxSoft.c

# Link locally-provided code into the support library,
# rather than directly into the IOC application.
# This is required for Windows DLL builds.
gpibSupport_SRCS += dbSubExample.c
gpibSupport_SRCS += gpibHello.c
gpibSupport_SRCS += initTrace.c

gpibSupport_LIBS += $(EPICS_BASE_IOC_LIBS)


# Build the IOC application
PROD_IOC = gpib
PROD_LIBS += asyn stream

# gpib.dbd will be created and installed
DBD += gpib.dbd

# gpib.dbd will include these files:
gpib_DBD += base.dbd
gpib_DBD += asyn.dbd
gpib_DBD += drvLinuxGpib.dbd
gpib_DBD += stream.dbd

# gpib_registerRecordDeviceDriver.cpp derives from gpib.dbd
gpib_SRCS += gpib_registerRecordDeviceDriver.cpp

# Build the main IOC entry point where needed
gpib_SRCS_DEFAULT += gpibMain.cpp
gpib_SRCS_vxWorks += -nil-

# Link in the code from our support library
gpib_LIBS += gpibSupport

# To build SNL programs, SNCSEQ must be defined
# in the <top>/configure/RELEASE file
ifneq ($(SNCSEQ),)
    # Build sncExample into gpibSupport
    sncExample_SNCFLAGS += +r
    gpib_DBD += sncExample.dbd
    # A .stt sequence program is *not* pre-processed:
    gpibSupport_SRCS += sncExample.stt
    gpibSupport_LIBS += seq pv
    gpib_LIBS += seq pv

    # Build sncProgram as a standalone program
    PROD_HOST += sncProgram
    sncProgram_SNCFLAGS += +m
    # A .st sequence program *is* pre-processed:
    sncProgram_SRCS += sncProgram.st
    sncProgram_LIBS += seq pv
    sncProgram_LIBS += $(EPICS_BASE_HOST_LIBS)
endif

# Finally link IOC to the EPICS Base libraries
gpib_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD EXTRA GNUMAKE RULES BELOW HERE

