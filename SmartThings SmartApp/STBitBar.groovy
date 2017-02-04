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
	unsubscribe()
	initialize()
}

def initialize() {
	// TODO: subscribe to attributes, devices, locations, etc.
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

// Respond to data requests
def getTempData() {
	log.debug "getTemps called"
	def resp = []
    temps.each {
        resp << [name: it.displayName, value: it.currentTemperature];
    }
    // Sort decending by temp value
    resp.sort { -it.value }
    log.debug "getTemps complete"
    return resp
}
def getContactData() {
	def resp = []
    contacts.each {
        resp << [name: it.displayName, value: it.currentContact];
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
def getMainDisplayData() {
	def resp = []
    resp << [name: displayTempName, value: displayTemp.currentTemperature];
    return resp
}
def getStatus() {
log.debug "getStatus called"
def tempData = getTempData()
def contactData = getContactData()
def switchData = getSwitchData()
def mainDisplay = getMainDisplayData()

def resp = [ "Temp Sensors" : tempData,
			 "Contact Sensors" : contactData,
             "Switches" : switchData,
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
			input "switches", "capability.switch",
				title: "Which Switches?",
				multiple: true,
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