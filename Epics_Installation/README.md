# epics IOC for keithley 2000 
gpib_test

# epics base, asyn, streamDevice are not here. 

They can be installed from the web sources.

git clone -b 3.15 https://git.launchpad.net/epics-base

git clone https://github.com/epics-modules/asyn.git

https://www.aps.anl.gov/BCDA/synApps/Where-to-find-it

R6_1 	8/16/19 	3.15.6 	synApps_6_1.tar.gz 	synApps_6_1 	synAppsReleaseNotes.html 	None

from synApps_6_1 to get StreamDevice-2-8-9

compile epics-base, support/asyn, support/StreamDevice2-8-9
