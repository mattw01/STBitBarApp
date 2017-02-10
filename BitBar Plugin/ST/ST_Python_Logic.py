# -*- coding: utf-8 -*-
import sys
import json
import subprocess
from subprocess import check_output
import ConfigParser
import re
import decimal
import time

##################################
# Set Required SmartApp Version
requiredVersion = 'v1.6'
##################################


# Define class for formatting numerical outputs (temp sensors)
# Define NumberFormatter class
class NumberFormatter:
    def __init__(self):
        self.decmialRounding = 0
        self.staticDecimalPlaces = -1

    def setRoundingPrecision(self, precision):
        self.decmialRounding = precision

    def setStaticDecimalPlaces(self, places):
        self.staticDecimalPlaces = places

    def getNumberOfDecimals(self, number):
        r = round(number, self.decmialRounding)
        if r % 1 == 0: return 0
        return abs(decimal.Decimal(str(r)).as_tuple().exponent)

    def formatNumber(self, number):
        r = round(number, self.decmialRounding)
        if self.staticDecimalPlaces is not -1:
            formatter = "{0:." + str(self.staticDecimalPlaces) + "f}"
            return formatter.format(r)
        else:
            if r % 1 == 0:
                return str(int(r))
            else:
                return str(r)
# End NumberFormatter

# Format percentages
def formatPercentage(val):
	if type(val) is int: return str(val) + "%"
	else: return val
# Format timespan values in milliseconds
def formatTimespan(ms):
	seconds=(timespan/1000)%60
	minutes=(timespan/(1000*60))%60
	hours=(timespan/(1000*60*60))%24
	timspanString = ''
	if hours > 0: timspanString += str(hours) + " hour"
	if hours > 1: timspanString += "s"
	timspanString += " " + str(minutes) + " minute"
	if minutes > 1: timspanString += "s"
	return timspanString
# Return hex color code based on multiple step gradient (for thermo colors)
def numberToColorGrad(val, color):
	if color == 'red':
		if val == 5: return "#E50008"
		if val == 4: return "#EB1B20"
		if val == 3: return "#F23739"
		if val == 2: return "#F85352"
		if val == 1: return "#FF6F6B"
		if val == 0: return "#FF757A"
	if color == 'blue':
		if val == 5: return "#002FE5"
		if val == 4: return "#1745EA"
		if val == 3: return "#2E5BEF"
		if val == 2: return "#4671F4"
		if val == 1: return "#5D87F9"
		if val == 0: return "#759DFF"
	return "green"

# Setting Class
class Setting(object):
    def __init__(self, cfg_path):
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(cfg_path)

    def get_setting(self, my_setting, default_value, severe_bool=False):
        try:
            ret = self.cfg.get("My Section", my_setting)
        except ConfigParser.NoOptionError as e:
            if severe_bool:
                print "Severe Error:" + str(e)
                raise SystemExit(0)
            else:
                ret = default_value
# Remove Extra Quotes, etc
        ret = re.sub(r'^"|"$', '', ret)
# Check Type and Convert as needed
        if   ret.lower()  =='true'  :   return True
        elif ret.lower()  =='false' :   return False
        elif ret.isdigit()          :   return int(ret)
        else:
            return ret
# End Class Setting

# Begin Read User Config File

cfgFileName                 = sys.argv[0][:-2] + "cfg"
cfgFileObj                  = Setting(cfgFileName)
cfgGetValue                 = cfgFileObj.get_setting
smartAppURL                 = cfgGetValue('smartAppURL'     , ""    , True)
secret                      = cfgGetValue('secret'          , ""    , True)
useImages                   = cfgGetValue('useImages'       , True)
sortSensors                 = cfgGetValue('sortSensors'     , True)
showSensorCount             = cfgGetValue('showSensorCount' , True)
presenscePresentEmoji       = cfgGetValue('presenscePresentEmoji'   , ":house:")
presensceNotPresentEmoji    = cfgGetValue('presensceNotPresentEmoji', ":x:")

# Main menu and sub-menu number of items settings
mainMenuMaxItemsDict = {"Temps"     : 99,
                        "Contacts"  : 99,
                        "Switches"  : 99,
                        "Motion"    : 99,
                        "Locks"     : 99,
                        "Presences" : 99
                        }
for sensorName in mainMenuMaxItemsDict:
    mainMenuMaxItemsDict[sensorName] = cfgGetValue('mainMenuMaxItems'+sensorName, '99')
# End Main menu and sub-menu format settings

subMenuMoreColor    = "color={}".format(cfgGetValue('subMenuMoreColor', 'black'))
# Read Temperature Formatting Settings
numberOfDecimals    = cfgGetValue('numberOfDecimals', "0")
matchOutputNumberOfDecimals = cfgGetValue('matchOutputNumberOfDecimals', False)

# End Read User Config File

# Set URLs
statusURL = smartAppURL + "GetStatus/"
switchURL = smartAppURL + "ToggleSwitch/?id="
levelURL = smartAppURL + "SetLevel/?id="
lockURL = smartAppURL + "ToggleLock/?id="
thermoURL = smartAppURL + "SetThermo/?id="

# Set the callback script for switch/level commands from parameters
callbackScript = sys.argv[1]


# Make the call the to the API and retrive JSON data
attempt = 0
maxRetries = 10
connected = False
while connected is False:
	try:
		output = check_output(['curl', '-s', statusURL, '-H', 'Authorization: Bearer ' + secret])
		connected = True
	except subprocess.CalledProcessError as grepexc:
		attempt += 1
		if attempt == maxRetries:
			print "No Connection"
			print "---"
			print "Please check connection and try again (⌘R)"
			print "Debug information: Error code ", grepexc.returncode, grepexc.output
			raise SystemExit(0)
		time.sleep(3)
		continue

# Parse the JSON data
j = json.loads(output)

# API Return Error Handling
if "error" in j:
    print "Error while communicating with ST API"
    print '---'
    if j['error'] == 'invalid_token':
        print "Please check your SmartApp URL and Secret are both correct and try again."
    print "Error Details: ", j['error']
    if "error_description" in j:
        print "Error Description: ", j['error_description']
    raise SystemExit(0)

# Get the sensor arrays from the JSON data
try:
  temps       = j['Temp Sensors']
  contacts    = j['Contact Sensors']
  switches    = j['Switches']
  motion      = j['Motion Sensors']
  mainDisplay = j['MainDisplay']
  locks       = j['Locks']
  presences   = j['Presence Sensors']
  thermostat = j['Thermostat']
except KeyError,e:
	print "Error in ST API Data"
	print "---"
	print "Error Details: ", e
	print "Source Data: ", output
	raise SystemExit(0)

# Sort sensors by name if option is enabled
if sortSensors is True:	
  temps       = sorted(temps, key=lambda k: k['name'])
  contacts    = sorted(contacts, key=lambda k: k['name'])
  switches    = sorted(switches, key=lambda k: k['name'])
  motion      = sorted(motion, key=lambda k: k['name'])
  mainDisplay = sorted(mainDisplay, key=lambda k: k['name'])
  locks       = sorted(locks, key=lambda k: k['name'])
  presences   = sorted(presences, key=lambda k: k['name'])

# Verify SmartApp Version	
try:
	ver = j['Version']
	if ver != requiredVersion:
		print "ST BitBar Version Error"
		print "---"
		print "Please make sure both Python and SmartThings SmartApp are up to date"
		print "Current Version:", ver
		print "Required Version:", requiredVersion
		raise SystemExit(0)
except KeyError,e:
	print "Error in ST API Data"
	print "---"
	print "Error Details: ", e
	print "Source Data: ", output
	raise SystemExit(0)

# Create a new NumberFormatter object
formatter = NumberFormatter()
# Set the number of decimals
formatter.setRoundingPrecision(numberOfDecimals)


# Format thermostat status color
thermoColor = ''
if len(thermostat) > 0:
	if "thermostatOperatingState" in thermostat[0]:
		if thermostat[0]['thermostatOperatingState'] == "heating":
			thermoColor = "|color=red"
		if thermostat[0]['thermostatOperatingState'] == "cooling":
			thermoColor = "|color=blue"


# Print the main display
degree_symbol = u'\xb0'.encode('utf8')
formattedMainDisplay = ''
# Check if there is a name
if mainDisplay[0]['name'] != None or mainDisplay[0]['name'] != "N/A":
	formattedMainDisplay += str(mainDisplay[0]['name'])
# Check if there is a value
if type(mainDisplay[0]['value']) is int or type(mainDisplay[0]['value']) is float:
	formattedMainDisplay += ":" + formatter.formatNumber(mainDisplay[0]['value']) + degree_symbol
print formattedMainDisplay

# Find the max length sensor so values are lined up correctly
maxLength = 0
maxDecimals = 0
for sensor in temps:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
    if formatter.getNumberOfDecimals(sensor['value']) > maxDecimals:
        maxDecimals = formatter.getNumberOfDecimals(sensor['value'])

for sensor in contacts:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in switches:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in motion:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
for sensor in locks:
    if len(sensor['name']) > maxLength:
        maxLength = len(sensor['name'])
# Increment maxLength by one since contact sensor icon needs to be pulled back a little
maxLength += 1

# Set the static amount of decimal places based on setting
if matchOutputNumberOfDecimals is True:
    formatter.setStaticDecimalPlaces(maxDecimals)
else:
    formatter.setStaticDecimalPlaces(-1)

# Output the seperation '---' between status bar items and menu items
print '---'

# Begin outputting sensor data

# Output Thermostat data
if len(thermostat) > 0:
	thermoImage = "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"
	if "thermostatMode" in thermostat[0] and\
	    "thermostatOperatingState" in thermostat[0]:
		setpointText = ''
		setpointAction = ' @ '
		# Set the action text based on operation state
		# Example: cooling to 75, idle @ 72, heating to 68
		if thermostat[0]['thermostatOperatingState'] == 'cooling' or\
		thermostat[0]['thermostatOperatingState'] == 'heating':
			setpointAction = ' to '
		currentSetpoint = 0
		# Pick the correction setpoint value
		if thermostat[0]['thermostatMode'] == 'cool':
			currentSetpoint = thermostat[0]['coolingSetpoint']
		if thermostat[0]['thermostatMode'] == 'heat':
			currentSetpoint = thermostat[0]['heatingSetpoint']
		# Set the display string
		setpointText = "(" + str(thermostat[0]['thermostatOperatingState']) + setpointAction + str(currentSetpoint) + degree_symbol + ")"
		if "displayName" in thermostat[0]: 
			print thermostat[0]['displayName'],setpointText,'|image=', thermoImage
		else: print "Thermostat Control",setpointText,'|image=', thermoImage
		print "--Current Status|font=Helvetica-Bold color=black size=14"
		if "thermostatMode" in thermostat[0]:
			print "--Mode:",thermostat[0]['thermostatMode']
		if "thermostatOperatingState" in thermostat[0]:
			print "--Status:",thermostat[0]['thermostatOperatingState']
		if "lastOperationEvent" in thermostat[0]:
			timespan = thermostat[0]['lastOperationEvent']
			seconds=(timespan/1000)%60
			minutes=(timespan/(1000*60))%60
			hours=(timespan/(1000*60*60))%24
			timspanString = str(hours) + ":" + str(minutes) + ":" + str(seconds)
			print "--Last Event:", formatTimespan(timespan), "ago"
		print "--Controls|font=Helvetica-Bold color=black size=14"
		currentThermoURL = thermoURL + thermostat[0]['id']
		thermoModeURL = currentThermoURL + "&type=mode&val="
		# Mode Menu
		if "thermostatMode" in thermostat[0]:
			print "--Mode"
			print "----Auto|bash=" + callbackScript + " param1=request param2=" + thermoModeURL + "auto" + " param3=" + secret 
			print "----Cool|bash=" + callbackScript + " param1=request param2=" + thermoModeURL + "cool" + " param3=" + secret 
			print "----Heat|bash=" + callbackScript + " param1=request param2=" + thermoModeURL + "heat" + " param3=" + secret 
			print "----Off|bash=" + callbackScript + " param1=request param2=" + thermoModeURL + "off" + " param3=" + secret 
		# Cooling Setpoint Menu
		if "coolingSetpoint" in thermostat[0]:
			coolSetpointURL = currentThermoURL + "&type=coolingSetpoint&val="
			currentCoolingSetPoint = thermostat[0]['coolingSetpoint']
			print "--Cooling Set Point (" + str(currentCoolingSetPoint) + degree_symbol + ")|color=blue"
			print "----Change Setpoint|size=9"
			for c in range(currentCoolingSetPoint - 5, currentCoolingSetPoint):
				id = currentCoolingSetPoint - c
				print "----",str(c)+degree_symbol,"|color=blue font=Helvetica-Bold color=",numberToColorGrad(id, "blue"),\
				"bash=", callbackScript, " param1=request param2=", str(coolSetpointURL + str(c)), " param3=", secret," terminal=false refresh=true"
			print "----", str(currentCoolingSetPoint)+degree_symbol,"(current)|color=",numberToColorGrad(0, "blue")
			for c in range(currentCoolingSetPoint + 1, currentCoolingSetPoint + 6):
				print "----",str(c)+degree_symbol,"|color=gray font=Helvetica-Bold",\
				"bash=", callbackScript, " param1=request param2=", str(coolSetpointURL + str(c)), " param3=", secret," terminal=false refresh=true"
		# Heating Setpoint Menu	
		if "heatingSetpoint" in thermostat[0]:
			heatingSetpointURL = currentThermoURL + "&type=heatingSetpoint&val="
			currentHeatingSetPoint = thermostat[0]['heatingSetpoint']
			print "--Heating Set Point (" + str(currentHeatingSetPoint) + degree_symbol + ")|color=red"
			print "----Change Setpoint|size=9"
			for c in range(currentHeatingSetPoint + 5, currentHeatingSetPoint, -1):
				id = c - currentHeatingSetPoint
				print "----",str(c)+degree_symbol,"|color=red font=Helvetica-Bold color=",numberToColorGrad(id, "red"),\
				"bash=", callbackScript, " param1=request param2=", str(heatingSetpointURL + str(c)), " param3=", secret," terminal=false refresh=true"
			print "----", str(currentHeatingSetPoint)+degree_symbol,"(current)|color=",numberToColorGrad(0, "red")
			for c in range(currentHeatingSetPoint - 1, currentHeatingSetPoint - 6, -1):
				print "----",str(c)+degree_symbol,"|color=gray font=Helvetica-Bold",\
				"bash=", callbackScript, " param1=request param2=", str(heatingSetpointURL + str(c)), " param3=", secret," terminal=false refresh=true"


# Output Temp Sensors
countSensors = len(temps)
if countSensors > 0:
    menuTitle = "Temp Sensors"
    mainTitle = menuTitle 
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle, "| font=Helvetica-Bold color=black size=15"
    colorSwitch = False
    mainMenuMaxItems = mainMenuMaxItemsDict["Temps"]
    subMenuText =''
    for i, sensor in enumerate(temps):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength): whiteSpace += ' '
        colorText = ''
        currentValue = formatter.formatNumber(sensor['value'])
        if colorSwitch == True: colorText = 'color=#333333'
        if colorSwitch == False: colorText = 'color=#666666'
        if i == mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"            
        print subMenuText, sensor['name'], whiteSpace, currentValue+degree_symbol, '|font=Menlo', colorText
        if "battery" in sensor:
			print subMenuText, sensor['name'], whiteSpace, formatPercentage(sensor['battery']), "|font=Menlo alternate=true",colorText
        colorSwitch = not colorSwitch

# Output Contact Sensors
countSensors = len(contacts)
if countSensors > 0:
    menuTitle = "Contact Sensors"
    mainTitle = menuTitle
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle,"|font=Helvetica-Bold color=black"
    mainMenuMaxItems = mainMenuMaxItemsDict["Contacts"]
    subMenuText =''
    for i, sensor in enumerate(contacts):
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
        if i == mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"            
        print subMenuText, sensor['name'], whiteSpace, sym, '|font=Menlo', colorText
        if "battery" in sensor:
			print subMenuText, sensor['name'], whiteSpace, formatPercentage(sensor['battery']), "|font=Menlo alternate=true",colorText
        colorSwitch = not colorSwitch


# Output Motion Sensors
countSensors = len(motion)
if countSensors > 0:
    menuTitle = "Motion Sensors"
    mainTitle = menuTitle
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle,"|font=Helvetica-Bold color=black"
    mainMenuMaxItems = mainMenuMaxItemsDict["Motion"]
    subMenuText =''
    for i, sensor in enumerate(motion):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength - 1): whiteSpace += ' '
        sym = ''
        if sensor['value'] == 'inactive':
            sym = '⇢⇠'
        else:
            sym = '⇠⇢'
        if colorSwitch == True: colorText = 'color=#333333'
        if colorSwitch == False: colorText = 'color=#666666'
        if i == mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"            
        print subMenuText, sensor['name'], whiteSpace, sym, '|font=Menlo', colorText
        if "battery" in sensor:
			print subMenuText, sensor['name'], whiteSpace, formatPercentage(sensor['battery']), "|font=Menlo alternate=true",colorText
        colorSwitch = not colorSwitch

# Output Presence Sensors
countSensors = len(presences)
if countSensors > 0:
    menuTitle = "Presence Sensors"
    mainTitle = menuTitle
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle, "|font=Helvetica-Bold color=black"
    mainMenuMaxItems = mainMenuMaxItemsDict["Presences"]
    subMenuText = ''
    for i, sensor in enumerate(presences):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        for x in range(0, extraLength - 1): whiteSpace += ' '
        sym = ''
        if sensor['value'] == 'present':
            emoji = presenscePresentEmoji
        else:
            emoji = presensceNotPresentEmoji
        if i >= mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"            
        print subMenuText, sensor['name'], whiteSpace, emoji, '|font=Menlo', colorText
        if "battery" in sensor:
			print subMenuText, sensor['name'], whiteSpace, formatPercentage(sensor['battery']), "|font=Menlo alternate=true",colorText
        colorSwitch = not colorSwitch

# Set base64 images for green locked/red unlocked
greenLocked = "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"
redUnlocked = "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"

# Output Locks
countSensors = len(locks)
if countSensors > 0:
    menuTitle = "Locks"
    mainTitle = menuTitle
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle,"|font=Helvetica-Bold color=black"
    mainMenuMaxItems = mainMenuMaxItemsDict["Locks"]
    subMenuText = ''
    for i, sensor in enumerate(locks):
        currentLockURL = lockURL + sensor['id']
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        img = ''
        sym = ''
        for x in range(0, extraLength - 1): whiteSpace += ' '
        if sensor['value'] == 'locked':
            sym = '🔒'
            img = greenLocked
        elif sensor['value'] == 'unlocked':
            sym = '🔓'
            img = redUnlocked
        else:
            sensor['name'] = sensor['name'] + "(" + sensor['value'] + ")"
        if i >= mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"   
        if useImages is True:
			print subMenuText, sensor[
				'name'], '|font=Menlo bash=', callbackScript, ' param1=request param2=', currentLockURL, ' param3=', secret, ' terminal=false refresh=true image=', img
        else:
			print subMenuText, sensor[
				'name'], whiteSpace, sym, '|font=Menlo bash=', callbackScript, ' param1=request param2=', currentLockURL, ' param3=', secret, ' terminal=false refresh=true'



# Set base64 images for status green/red
greenImage = "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"
redImage = "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"

# Output Switches
countSensors = len(switches)
if countSensors > 0:
    menuTitle = "Switches"
    mainTitle = menuTitle
    if showSensorCount == True: mainTitle += " ("+str(countSensors)+")"
    print mainTitle,"|font=Helvetica-Bold color=black"
    mainMenuMaxItems = mainMenuMaxItemsDict["Switches"]
    subMenuText = ''
    for i, sensor in enumerate(switches):
        currentLength = len(sensor['name'])
        extraLength = maxLength - currentLength
        whiteSpace = ''
        img = ''
        for x in range(0, extraLength): whiteSpace += ' '
        if sensor['value'] == 'on':
            sym = '🔛'
            img = greenImage
        else:
            sym = '🔴'
            img = redImage
        currentSwitchURL = switchURL + sensor['id']
        if i == mainMenuMaxItems:
			print "{} More... | {}".format(countSensors-mainMenuMaxItems, subMenuMoreColor)
			print "-- " + menuTitle + " ("+str(countSensors-mainMenuMaxItems)+")"
			subMenuText = "--"       
        if useImages is True:
            print subMenuText, sensor[
                'name'], '|font=Menlo bash=', callbackScript, ' param1=request param2=', currentSwitchURL, ' param3=', secret, ' terminal=false refresh=true image=', img
        else:
            print subMenuText, sensor[
                'name'], whiteSpace, sym, '|font=Menlo bash=', callbackScript, ' param1=request param2=', currentSwitchURL, ' param3=', secret, ' terminal=false refresh=true'
        if sensor['isDimmer'] is True:
            print str(str(subMenuText) + "--"), 'Set Dimmer Level|size=9'
            currentLevel = 10
            while True:
                currentLevelURL = levelURL + sensor['id'] + '&level=' + str(currentLevel)
                print str(subMenuText + "--"), currentLevel, '%| bash=', callbackScript, ' param1=request param2=', currentLevelURL, ' param3=', secret, ' terminal=false refresh=true'
                if currentLevel is 100:
                    break
                currentLevel += 10
