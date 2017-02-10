/**
 *  BitBar Output App
 *
 *  Copyright 2016 mattw
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *  in compliance with the License. You may obtain a copy of the License at:
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 *  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
 *  for the specific language governing permissions and limitations under the License.
 *
 */
 
 // V 1.0 Initial release
 // V 1.1 Added logging from @kurtsanders making it easier to copy/paste URL and secret
 // V 1.2 Add extra handling if Main Display is not set (right now N/A is displayed)
 // V 1.3 Add Lock capability support
 // V 1.4 Add Thermostat selection and battery data output
 // V 1.5 Add Thermostat control options and version verification
 
def version() { return "v1.5" }
definition(
    name: "BitBar Output App",
    namespace: "mattwz",
    author: "mattw",
    description: "Logic for outputting BitBar data",
    category: "",
    iconUrl: "https://github.com/mattw01/STBitBarApp/raw/master/STBB60.png",
    iconX2Url: "https://github.com/mattw01/STBitBarApp/raw/master/STBB120.png",
    iconX3Url: "https://github.com/mattw01/STBitBarApp/raw/master/STBB120.png")


preferences {
  page(name:"mainPage")
  page(name:"devicesPage")
  page(name:"disableAPIPage")
  page(name:"enableAPIPage")
  section ("Display Sensor") {
  input "displayTempName", "string", multiple: false, required: false
    input "displayTemp", "capability.temperatureMeasurement", multiple: false, required: false
  }
  section ("Allow external service to get the temperature ...") {
    input "temps", "capability.temperatureMeasurement", multiple: true, required: false
  }
  section ("Allow external service to get the contact status ...") {
    input "contacts", "capability.contactSensor", multiple: true, required: false
  }
  section ("Allow external service to get the switches ...") {
    input "switches", "capability.switch", multiple: true, required: false
  }
  section ("Allow external service to get the thermostat status ...") {
    input "thermos", "capability.thermostat", multiple: true, required: false
  }
  section ("Allow external service to get the motion status ...") {
    input "motions", "capability.motionSensor", multiple: true, required: false
  }
  section ("Allow external service to get the presence status ...") {
    input "presences", "capability.presenceSensor", multiple: true, required: false
  }
}
mappings {

  path("/GetStatus/") {
    action: [
      GET: "getStatus"
    ]
  }
  path("/ToggleSwitch/") {
    action: [
      GET: "toggleSwitch"
    ]
  }
  path("/SetLevel/") {
    action: [
      GET: "setLevel"
    ]
  }
    path("/SetThermo/") {
    action: [
      GET: "setThermo"
    ]
  }
  path("/ToggleLock/") {
    action: [
      GET: "toggleLock"
    ]
  }
}
def installed() {
	log.debug "Installed with settings: ${settings}"

	initialize()
}
def uninstalled() {
	if (state.endpoint) {
		try {
			logDebug "Revoking API access token"
			revokeAccessToken()
		}
		catch (e) {
			log.warn "Unable to revoke API access token: $e"
		}
	}
}
def updated() {
	// Added additional logging from @kurtsanders
	log.debug "Bitbar Outout App updated with the following settings:\n${settings}"
    log.debug "##########################################################################################"
    log.debug "secret = \"${state.endpointSecret}\""
    log.debug "smartAppURL = \"${state.endpointURL}\""
    log.debug "The API has been setup. Please enter the following two lines into the ST BitBar Python script in your plugins directory."
    log.debug "##########################################################################################"

	unsubscribe()
	initialize()
}

def initialize() {
	if(thermo)
		subscribe(thermo, "thermostatOperatingState", thermostatOperatingStateHandler)
    state.lastThermostatOperatingState = now()
	// TODO: subscribe to attributes, devices, locations, etc.
}
def thermostatOperatingStateHandler(evt) {
	log.debug "thermostatOperatingStateHandler received event" 
	state.lastThermostatOperatingState = now()
}


// Respond to action requests
def toggleSwitch() {
	def command = params.id
	log.debug "toggleSwitch called with id ${command}"
    
    switches.each {
    	if(it.id == command)
        {
        	log.debug "Found switch ${it.displayName} with id ${it.id} with current value ${it.currentSwitch}"
            if(it.currentSwitch == "on")
            	it.off()
            else
            	it.on()
            return
		}
    }
    log.debug "Woah Nelly! We didn't find a switch with id ${command}. Uh Oh..."
}
def setLevel() {
	def command = params.id
    def level = params.level
	log.debug "toggleSwitch called with id ${command} and level ${level}"
    
    switches.each {
    	if(it.id == command)
        {
        	log.debug "Found switch ${it.displayName} with id ${it.id} with current value ${it.currentSwitch}"
            def fLevel = Float.valueOf(level)
            log.debug "Setting level to ${fLevel}"
            it.setLevel(fLevel)
            return
		}
    }
    log.debug "Good Goolly Miss Molly! We didn't find a switch with id ${command}. Uh Oh..."
}
def setThermo() {
	def id = params.id
    def cmdType = params.type
    def val = params.val
	log.debug "setThermo called with id ${id} command ${cmdType} and value ${cmdType}"
    
    if(thermo) {
    	if(thermo.id == id) {
        	if(cmdType == "mode") {
            	if(val == "auto") {
                	log.debug "Setting thermo to auto"
                    thermo.auto()
                }
            	if(val == "heat") {
                	log.debug "Setting thermo to heat"
                    thermo.heat()
                }
            	if(val == "cool") {
                	log.debug "Setting thermo to cool"
                    thermo.cool()
                }
            	if(val == "off") {
                	log.debug "Setting thermo to off"
                    thermo.off()
                }
            }
        	if(cmdType == "heatingSetpoint") {
            	log.debug "Setting Heat Setpoint to ${val}"
            	thermo.setHeatingSetpoint(val)
            }
        	if(cmdType == "coolingSetpoint") {
            	log.debug "Setting Cool Setpoint to ${val}"
            	thermo.setCoolingSetpoint(val)
            }
        }
    }
}
def toggleLock() {
	def command = params.id
	log.debug "toggleLock called with id ${command}"
    
    locks.each {
    	if(it.id == command)
        {
        	log.debug "Found lock ${it.displayName} with id ${it.id} with current value ${it.currentLock}"
            if(it.currentLock == "locked")
            	it.unlock()
            else if(it.currentLock == "unlocked")
            	it.lock()
            else
            	log.debug "Non-supported toggle state for lock ${it.displayName} state ${it.currentLock} let's not do anything"
            return
		}
    }
    log.debug "Hey there now! We didn't find a lock with id ${command}. Uh Oh..."
}

def getBatteryInfo(dev) {
	if(dev.currentBattery) return "${dev.currentBattery}%"
    else return "N/A"
}

// Respond to data requests
def getTempData() {
	log.debug "getTemps called"
	def resp = []
    temps.each {
        resp << [name: it.displayName, value: it.currentTemperature, battery: getBatteryInfo(it)];
    }
    // Sort decending by temp value
    resp.sort { -it.value }
    log.debug "getTemps complete"
    return resp
}
def getContactData() {
	def resp = []
    contacts.each {
        resp << [name: it.displayName, value: it.currentContact, battery: getBatteryInfo(it)];
    }
    return resp
}
def getPresenceData() {
	def resp = []
    presences.each {
        resp << [name: it.displayName, value: it.currentPresence];
    }
    return resp
}
def getMotionData() {
	def resp = []
    motions.each {
        resp << [name: it.displayName, value: it.currentMotion];
    }
    return resp
}
def getSwitchData() {
	def resp = []
    switches.each {
    	def isDimmer = false
        def currentName = it.displayName
    	if(it.currentLevel) {
        	isDimmer = true
            if(it.currentSwitch == 'on') currentName += " (" + it.currentLevel + "%)"
        }
        
        resp << [name: currentName, value: it.currentSwitch, id : it.id, isDimmer : isDimmer];
    }
    return resp
}
def getLockData() {
	def resp = []
    locks.each {
        resp << [name: it.displayName, value: it.currentLock, id : it.id, battery: getBatteryInfo(it)];
    }
    return resp
}
def getThermoData() {

	def resp = []
    if(thermo) {
    	def timespan = now() - state.lastThermostatOperatingState
    	resp << [displayName: thermo.displayName,
        		id: thermo.id,
        		thermostatOperatingState: thermo.currentThermostatOperatingState,
        		thermostatMode: thermo.currentThermostatMode,
                coolingSetpoint: thermo.currentCoolingSetpoint,
                heatingSetpoint: thermo.currentHeatingSetpoint,
                lastOperationEvent: timespan
                ];
    }
    return resp
}
def getMainDisplayData() {
	def returnName;
    def returnValue;
    
    if(displayTempName) returnName = displayTempName
    else returnName = "N/A"
    if(displayTemp) returnValue = displayTemp.currentTemperature
    else returnValue = "N/A"
    
	def resp = []
    resp << [name: returnName, value: returnValue];
    return resp
}
def getStatus() {
log.debug "getStatus called"
def tempData = getTempData()
def contactData = getContactData()
def presenceData = getPresenceData()
def motionData = getMotionData()
def switchData = getSwitchData()
def lockData = getLockData()
def thermoData = getThermoData()
def mainDisplay = getMainDisplayData()

def resp = [ "Version" : version(),
			 "Temp Sensors" : tempData,
			 "Contact Sensors" : contactData,
			 "Presence Sensors" : presenceData,
			 "Motion Sensors" : motionData,
             "Switches" : switchData,
             "Locks" : lockData,
             "Thermostat" : thermoData,
             "MainDisplay" : mainDisplay]

log.debug "getStatus complete"
return resp

}


private mainPage() {	
	dynamicPage(name: "mainPage", uninstall:true, install:true) {
		section("API Setup") {
			if (state.endpoint) {
					paragraph "API has been setup. Please enter the following information into the ST BitBar Python script."
                    paragraph "URL:\n${state.endpointURL}"
                    paragraph "Secret:\n${state.endpointSecret}"
                    href "disableAPIPage", title: "Disable API", description: ""
			}
            else {
			paragraph "API has not been setup. Tap below to enable it."	
            href name: "enableAPIPageLink", title: "Enable API", description: "", page: "enableAPIPage"
            }
            
		}
        section("Device Setup") {
        href name: "devicesPageLink", title: "Select Devices", description: "", page: "devicesPage"
        }
	}
}


def disableAPIPage() {	
	dynamicPage(name: "disableAPIPage", title: "") {
		section() {
			if (state.endpoint) {
				try {
					revokeAccessToken()
				}
				catch (e) {
					log.debug "Unable to revoke access token: $e"
				}
				state.endpoint = null
			}	
			paragraph "It has been done. Your token has been REVOKED. You're no longer allowed in API Town (I mean, you can always have a new token). Tap Done to continue."	
		}
	}
}

def enableAPIPage() {
	dynamicPage(name: "enableAPIPage") {
		section() {
			if (initializeAppEndpoint()) {
				paragraph "Woo hoo! The API is now enabled. Brace yourself, though. I hope you don't mind typing long strings of gobbledygook. Sorry I don't know of an easier way to transfer this to the PC. Anyways, tap Done to continue"
			} 
			else {
				paragraph "It looks like OAuth is not enabled. Please login to your SmartThings IDE, click the My SmartApps menu item, click the 'Edit Properties' button for the BitBar Output App. Then click the OAuth section followed by the 'Enable OAuth in Smart App' button. Click the Update button and BAM you can finally tap Done here.", title: "Looks like we have to enable OAuth still", required: true, state: null
			}
		}
	}
}



def devicesPage() {
	dynamicPage(name:"devicesPage") {	
    
        section("Status Bar Title Device") {
        paragraph "Enter the short name for the device you want displayed as the main status bar item and choose the device"
			input "displayTempName", "string",
				title: "Display Name",
				multiple: false,
				required: false		
			input "displayTemp", "capability.temperatureMeasurement",
				title: "Display Sensor",
				multiple: false,
				hideWhenEmpty: true,
				required: false		
        }
        
		section ("Choose Devices") {
			paragraph "Select devices that you want to be displayed in the menubar."
			input "temps", "capability.temperatureMeasurement",
				title: "Which Temperature Sensors?",
				multiple: true,
				hideWhenEmpty: true,
				required: false
			input "contacts", "capability.contactSensor",
				title: "Which Contact Sensors?",
				multiple: true,
				hideWhenEmpty: true,
				required: false                
			input "motions", "capability.motionSensor",
				title: "Which Motion Sensors?",
				multiple: true,
				hideWhenEmpty: true,
				required: false                
			input "switches", "capability.switch",
				title: "Which Switches?",
				multiple: true,
				hideWhenEmpty: true,
				required: false	
			input "locks", "capability.lock",
				title: "Which Locks?",
				multiple: true,
				hideWhenEmpty: true,
				required: false	
			input "presences", "capability.presenceSensor",
				title: "Which Presence Sensors?",
				multiple: true,
				hideWhenEmpty: true,
				required: false                
			input "thermo", "capability.thermostat",
				title: "Which Thermostat?",
				multiple: false,
				hideWhenEmpty: true,
				required: false	
		}

	}
}


private initializeAppEndpoint() {	
	if (!state.endpoint) {
		try {
			def accessToken = createAccessToken()
			if (accessToken) {
				state.endpoint = apiServerUrl("/api/token/${accessToken}/smartapps/installations/${app.id}/")	
                state.endpointURL = apiServerUrl("/api/smartapps/installations/${app.id}/")	
                state.endpointSecret = accessToken
			}
		} 
		catch(e) {
			state.endpoint = null
		}
	}
	return state.endpoint
}
