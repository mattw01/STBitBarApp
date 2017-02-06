# STBitBarApp
SmartThings BitBar App

## Overview:
Monitor SmartThings sensors from the Apple OSX Menu Bar. Currently it works for displaying temperature and contact sensors, and controlling switch/dimmer level devices. This is all I really need, but there’s definitely more possibilities (presence sensors, controlling thermostats, etc). If there’s interest I can add more devices and features, or anyone in the community is welcome to modifying it.

## Section 1: Installation:
Section 1: Making the SmartApp available via the IDE

1. Setup the SmartApp: Find your [SmartThings IDE link](https://graph.api.smartthings.com/) I’m not sure what the second US shard address is off the top of my head.
2. Click My SmartApps > then New SmartApp (top-right green button)
3. Click the From Code tab and paste the [SmartApp code from GitHub](https://raw.githubusercontent.com/mattw01/STBitBarApp/master/SmartThings%20SmartApp/STBitBar.groovy) then click Create (I know there’s GitHub integrations, feel free to do it that way if you know how)
4. Enable OAuth: Back at the My SmartApps page, click the little edit icon for the BitBar Output App, then click OAuth section, then click Enable OAuth in SmartApp

## Section 2: Installing the SmartApp

1. Now for actually installing the SmartApp: On your mobile device in the SmartThings app > tap Automation > SmartApps > + Add a SmartApp (at the bottom). Go down to My Apps > select BitBar Output App.
2. Open the IDE [Live Logging](https://graph.api.smartthings.com/ide/logs) in a separate browser tab. 
3. Tap to Enable the API then tap Done. You should have a URL and secret displayed in the Live Logging screen tab. 
4. Copy/Save these to input in the BitBar script in the step ahead.
5. Select Devices: choose the devices you want to display/control then tap Done.

## Section 3: Setting up BitBar and ST Plugin

1. Download and install the [BitBar app](https://github.com/matryer/bitbar/releases/tag/v1.9.2)
2. IMPORTANT: When selecting a plugin directory, make sure you create one that does not contain spaces. There were issues in an older release of BitBar if the path contained spaces, but supposedly it’s fixed, but I still had issues in some cases. If there were no spaces, it always worked.
3. Download the [ST plugin from GitHub](https://github.com/mattw01/STBitBarApp/tree/master/BitBar%20Plugin). Copy **ONLY** the ST.5m.sh file to the plugin directory you specified along with the ST subfolder containing the Python script (make sure this stays in the folder named ST).  These shoud be the only files in the plugins directory.
4. Add your URL and secret to the Python script: Open the script with a text editor of your choice. put the URL that was displayed in step 5 in the smartAppURL variable and Secret in the secret variable. Save the script.
6. Start the BitBar app and you should see your status’ in the menubar!

## Issues / Limitations:
1. I know calling cURL via Python is not the best thing to do, but I wanted to make it as simple as possible using the built-in Python available in macOS/OSX. It would be better to use the requests library, but this requires setting up a new Python installation.
2. Typing the API URL and token from the SmartApp is sort of a pain but right now I don't know of any easy way to copy it over (open to any suggestions).
3. BitBar is capable of cycling through multiple status bar items, but all I really needed was to display one temperature sensor at the top with the rest in the dropdown. So the app only allows a selection of one temp sensor and a custom title (I didn’t want to use the full sensor name since menubar real estate is top dollar)
4. I’m not exactly happy with using emojis for the on/off status’ but there is the possibility of encoding an image into the output so maybe I can change that at some point.
5. There is no alignment supported by BitBar so it’s all done by character spacing, which means using monospace fonts. Which also means a limited selection of pretty looking fonts. Menlo works good enough for me, but feel free to change it.

I’m open to any feedback or suggestions/features! Let me know what you think!
