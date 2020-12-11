TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS BELOW HERE

# Install databases, templates & substitutions like this
#DB += dbExample1.db
#DB += dbExample2.db
#DB += dbSubExample.db
#DB += user.substitutions

#first time I just use yourdev.db, successfully.
DB += yourdev.db

#seconde try using below, failed.
DB += Keithley2000.substitutions
DB += Keithley2000Main.template
DB += keithleyHHL.db
DB += Keithley2000.proto

# If <anyname>.db template is not named <anyname>*.template add
# <anyname>_TEMPLATE = <templatename>

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD EXTRA GNUMAKE RULES BELOW HERE

