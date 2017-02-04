# -*- coding: utf-8 -*-
import sys
import json
import subprocess
from subprocess import check_output

##########################################################################################
## USER INPUT ############################################################################
## Enter your SmartApp URL and Secret below ##############################################
##########################################################################################

smartAppURL = "https://graph.api.smartthings.com/api/smartapps/installations/[Your SmartAppID]"
secret = "Your Secret Goes Here"

##########################################################################################
## END USER INPUT ########################################################################
##########################################################################################


#Set URLs
statusURL = smartAppURL + "GetStatus/"
switchURL = smartAppURL + "ToggleSwitch/?id="
levelURL =  smartAppURL + "SetLevel/?id="

# Set the callback script for switch/level commands from parameters
callbackScript = sys.argv[1]

# Make the call the to the API and retrive JSON data
try:
   output = check_output(['curl', '-s', statusURL, '-H', 'Authorization: Bearer ' + secret])                     
except subprocess.CalledProcessError as grepexc:                                                                                                   
    print "No Connection"
    print "---"
    print "Please check connection and try again"
    print "Debug information: Error code ",grepexc.returncode, grepexc.output
    raise SystemExit(0)

# Parse the JSON data
j = json.loads(output)

# Get the sensor arrays from the JSON data
temps =       j['Temp Sensors']
contacts =    j['Contact Sensors']
switches =    j['Switches']
mainDisplay = j['MainDisplay']

# Print the main display
print mainDisplay[0]['name'],':',mainDisplay[0]['value']

# Find the max length sensor so values are lined up correctly
maxLength = 0
for sensor in temps:
	if len(sensor['name']) > maxLength:
		maxLength = len(sensor['name'])
		
for sensor in contacts:
	if len(sensor['name']) > maxLength:
		maxLength = len(sensor['name'])	
		
for sensor in switches:
	if len(sensor['name']) > maxLength:
		maxLength = len(sensor['name'])	
# Increment maxLength by one since contact sensor icon needs to be pulled back a little
maxLength += 1

# Output the seperation '---' between status bar items and menu items 
print '---'

# Begin outputting sensor data

# Output Temp Sensors
if len(temps) > 0: print "Temp Sensors|font=Helvetica-Bold color=black size=15"
colorSwitch = False
for sensor in temps:
	currentLength = len(sensor['name'])
	extraLength = maxLength - currentLength
	whiteSpace = ''
	for x in range(0, extraLength): whiteSpace += ' '
	colorText = ''
	currentValue = sensor['value']
	if type(currentValue) is float:
		currentValue = int(currentValue)
		
	if colorSwitch == True: colorText = 'color=#333333'
	if colorSwitch == False: colorText = 'color=#666666'
	print sensor['name'], whiteSpace, currentValue, '|font=Menlo', colorText
	colorSwitch = not colorSwitch	

#Output Contact Sensors	
if len(contacts) > 0: print "Contact Sensors|font=Helvetica-Bold color=black"
for sensor in contacts:
	currentLength = len(sensor['name'])
	extraLength = maxLength - currentLength
	whiteSpace = ''
	for x in range(0, extraLength - 1): whiteSpace += ' '
	sym = ''
	if sensor['value'] == 'closed':
		sym = '⇢⇠'
	else:
		sym = '⇠⇢'
	if colorSwitch == True: colorText = 'color=#333333'
	if colorSwitch == False: colorText = 'color=#666666'
	print sensor['name'], whiteSpace, sym , '|font=Menlo', colorText
	colorSwitch = not colorSwitch
	
#Output Switches	
if len(switches) > 0: print "Switches|font=Helvetica-Bold color=black"
for sensor in switches:
	currentLength = len(sensor['name'])
	extraLength = maxLength - currentLength
	whiteSpace = ''
	for x in range(0, extraLength): whiteSpace += ' '
	if sensor['value'] == 'on':
		sym = '🔛'
	else:
		sym = '🔴'
	currentSwitchURL = switchURL + sensor['id']
	print sensor['name'], whiteSpace, sym , '|font=Menlo bash=',callbackScript,' param1=request param2=',currentSwitchURL,' param3=',secret,' terminal=false refresh=true'
	if sensor['isDimmer'] is True:
		print '-- Set Dimmer Level|size=9'
		currentLevel = 10
		while True:
			currentLevelURL = levelURL + sensor['id'] + '&level=' + str(currentLevel)
			print '-- ',currentLevel,'%| bash=',callbackScript,' param1=request param2=',currentLevelURL,' param3=',secret,' terminal=false refresh=true'
			if currentLevel is 100:
				break
			currentLevel += 10
