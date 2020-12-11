# epics IOC for keithley 2000 
gpib_test

# epics base, asyn, streamDevice are not here. 

They can be installed from the web sources.

git clone -b 3.15 https://git.launchpad.net/epics-base

git clone https://github.com/epics-modules/asyn.git

https://www.aps.anl.gov/BCDA/synApps/Where-to-find-it

R6_1 	8/16/19 	3.15.6 	synApps_6_1.tar.gz 	synApps_6_1 	synAppsReleaseNotes.html 	None

from synApps_6_1 to get StreamDevice-2-8-9

# Tree: 
epics-base: /usr/local/epics/epics-base
asyn: /usr/local/epics/support/asyn
streamDevice: /usr/local/epics/support/StreamDevice


compile epics-base, support/asyn, support/StreamDevice2-8-9 above. 

## gpib_test IOC
My application is under : /home/pi/gpib_test

we can also put the applications under /usr/local/epics/ioc, then all things are under /usr/local/epics.

