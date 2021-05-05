
import os, subprocess, platform
from os import listdir
from os.path import isfile, join
from pathlib import Path


washer = indigo.devices[209261100]
dryer = indigo.devices[921498561]

stateOff = 0
stateIdle = 1
stateOn = 2


indigo.device.resetEnergyAccumTotal(209261100)

for key in washer.states.keys():
	indigo.server.log(key)
current_dryer = dryer.states['curEnergyLevel']
current_washer = washer.states['curEnergyLevel']
if current_dryer >= 2:

indigo.server.log(str(current_dryer))
