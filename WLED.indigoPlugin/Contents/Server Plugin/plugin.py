#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2019 neilk
#
# Based on the sample dimmer plugin

################################################################################
# Imports
################################################################################
import indigo
import requests
import json

################################################################################
# Globals
################################################################################
theUrlBase = u"/json"

########################################
# Function to validate IP address
########################################
def validate_ipaddress(ipstring):
    a = ipstring.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True



################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    # Class properties
    ########################################

    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get("showDebugInfo", False)
        self.deviceList = []


    ########################################
    def deviceStartComm(self, device):
        self.debugLog("Starting device: " + device.name)
        self.debugLog(str(device.id)+ " " + device.name)
        if device.id not in self.deviceList:
            self.update(device)
            self.deviceList.append(device.id)



    ########################################
    def deviceStopComm(self, device):
        self.debugLog("Stopping device: " + device.name)
        if device.id in self.deviceList:
            self.deviceList.remove(device.id)

    ########################################
    def runConcurrentThread(self):
        self.debugLog("Starting concurrent thread")
        pollingFreq = int(self.pluginPrefs['pollingFrequency'])
        try:
            while True:
                # we sleep (by a user defined amount, default 60s) first because when the plugin starts, each device
                # is updated as they are started.
                self.sleep(1 * pollingFreq )
                # now we cycle through each WLED
                for deviceId in self.deviceList:
                    # call the update method with the device instance
                    self.update(indigo.devices[deviceId])
        except self.StopThread:
                pass

    ########################################
    def update(self,device):
        self.debugLog("Updating device: " + device.name)
        requestsTimeOut = float(self.pluginPrefs.get('requeststimeout'))
        theUrl = u"http://%s/json" % device.pluginProps[u"ipaddress"]   # Python 2.7 Style
        try:
            response = requests.get(theUrl, timeout=requestsTimeOut)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.errorLog("HTTP error getting %s %s data: %s" % (device.name,device.pluginProps["ipaddress"], str(e)))
            device.setErrorStateOnServer('Not Responding')
            return
        except Exception, e:
            self.errorLog("Unknown error getting %s %s data: %s" % (device.name,device.pluginProps["ipaddress"], str(e)))
            device.setErrorStateOnServer('Not Responding')
            return
        #Get the JSON from the WLED to update device states
        statusjson = json.loads(response.text)
        wledeffects = statusjson['effects']
        wledpalettes = statusjson['palettes']
        #Un comment below to help diagnose JSON state changes for testing
        #self.debugLog(statusjson)
        # parse out the elements which I know is really ugly, I will sort this to do it properly I promise

        #calculate the UI adjusted brightness to match the UI (0 -100 %) versus 0-255 for device
        adjustedbrightness = int(round(int(statusjson['state']['bri'])/2.55))
        #Update Device States
        # First two may be useful in the future, as WLED will support multiple segments in a single controller
        device.updateStateOnServer("WLEDversion", statusjson['info']['ver'])
        device.updateStateOnServer("WLEDfreeheap", statusjson['info']['freeheap'])
        # Now for the useful states
        device.updateStateOnServer("brightness", statusjson['state']['bri'])
        device.updateStateOnServer("brightnessLevel",adjustedbrightness)
        device.updateStateOnServer("onOffState", statusjson['state']['on'])
        device.updateStateOnServer("preset", statusjson['state']['ps'])
        device.updateStateOnServer("transition", statusjson['state']['transition'])
        # For the Palette we will also set a matching palette name
        device.updateStateOnServer("palette", statusjson['state']['seg'][0]['pal'])
        device.updateStateOnServer("palettename", wledpalettes[statusjson['state']['seg'][0]['pal']])
        device.updateStateOnServer("playlist", statusjson['state']['pl'])
        # For the effect we will also find the matching state name from the list
        device.updateStateOnServer("effect", statusjson['state']['seg'][0]['fx'])
        device.updateStateOnServer("effectname", wledeffects[statusjson['state']['seg'][0]['fx']])
        device.updateStateOnServer("effectintensity", statusjson['state']['seg'][0]['ix'])
        device.updateStateOnServer("effectspeed", statusjson['state']['seg'][0]['sx'])
        device.updateStateOnServer("nightlight", statusjson['state']['nl']['on'])
        device.updateStateOnServer("nightlightduration", statusjson['state']['nl']['dur'])
        device.updateStateOnServer("primarybluevalue", statusjson['state']['seg'][0]['col'][0][2])
        device.updateStateOnServer("primaryredvalue", statusjson['state']['seg'][0]['col'][0][0])
        device.updateStateOnServer("primarygreenvalue", statusjson['state']['seg'][0]['col'][0][1])
        device.updateStateOnServer("secondarybluevalue", statusjson['state']['seg'][0]['col'][1][2])
        device.updateStateOnServer("secondaryredvalue", statusjson['state']['seg'][0]['col'][1][0])
        device.updateStateOnServer("secondarygreenvalue", statusjson['state']['seg'][0]['col'][1][1])
        device.updateStateOnServer("UDPsend", statusjson['state']['udpn']['send'])
        device.updateStateOnServer("UDPrecv", statusjson['state']['udpn']['recv'])



    ########################################
    # UI Validate, Close, and Actions defined in Actions.xml:
    ########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        if not(validate_ipaddress(valuesDict['ipaddress'])):
            errorsDict = indigo.Dict()
            errorsDict['ipaddress'] = "Incorrectly formed or invalid IP address"
            self.errorLog("Incorrectly formed or invalid IP address")
            return (False, valuesDict, errorsDict)


        wledIP = valuesDict['ipaddress']
        valuesDict['ipaddress'] = wledIP
        valuesDict['address'] = wledIP
        theUrl = u"http://"+ wledIP+ theUrlBase


        try:
            r = requests.get(theUrl, timeout=1)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            errorsDict = indigo.Dict()
            errorsDict['ipaddress'] = "WLED not found or isn't responding"
            self.errorLog("Error getting WLED data: %s" % wledIP)
            return (False, valuesDict, errorsDict)
        except Exception, e:
            errorsDict = indigo.Dict()
            errorsDict['ipaddress'] = "Unknown error connecting to WLED"
            self.errorLog("Unknown Error getting WLED data: %s Check IP address" % wledIP)
            return (False, valuesDict, errorsDict)

        return (True, valuesDict)


    ########################################
    # UI Validate, Plugin Preferences
    ########################################
    def validatePrefsConfigUi(self, valuesDict):
        try:
            timeoutint=float(valuesDict['requeststimeout'])
        except:
            self.errorLog("Invalid entry for  WLED Plugin Config API Timeout - must be a number")
            errorsDict = indigo.Dict()
            errorsDict['requeststimeout'] = "Invalid entry for  WLED Plugin Config API Timeout - must be a number"
            return (False, valuesDict, errorsDict)
        try:
            pollingfreq=int(valuesDict['pollingFrequency'])
        except:
            self.errorLog("Invalid entry for WLED Plugin Config Polling Frequency - must be a whole number greater than 0")
            errorsDict = indigo.Dict()
            errorsDict['pollingFrequency'] = "Invalid entry for WLED Plugin Config Polling Frequency - must be a whole number greater than 0"
            return (False, valuesDict, errorsDict)

        if int(valuesDict['pollingFrequency']) == 0:
            self.errorLog("Invalid entry for WLED Plugin Config Polling Frequency - must be greater than 0")
            errorsDict = indigo.Dict()
            errorsDict['pollingFrequency'] = "Invalid entry for WLED Plugin Config Polling Frequency - must be a whole number greater than 0"
            return (False, valuesDict, errorsDict)
        if int(valuesDict['requeststimeout']) == 0:
            self.errorLog("Invalid entry for WLED Plugin Config Requests Timeout - must be greater than 0")
            errorsDict = indigo.Dict()
            errorsDict['requeststimeout'] = "Invalid entry for WLED Plugin Config Requests Timeout - must be greater than 0"
            return (False, valuesDict, errorsDict)

        #Otherwise we are good
        return (True, valuesDict)

    ########################################
    # UI Validate, Actions
    ########################################
    def validateActionConfigUi(self, valuesDict, typeId, deviceId):
        self.debugLog(valuesDict)
        # Validate Intensity
        if 'effectintensity' in valuesDict:
            try:
                effectintensity=int(valuesDict['effectintensity'])
            except:
                self.errorLog("Invalid entry for Effect Intensity - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['effectintensity'] = "Invalid entry for Effect Intensity - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['effectintensity']))
            if  not(int(valuesDict['effectintensity']) in xrange(0,256)):

            #if 0 <= int(valuesDict['effectintensity']) >= 256:
                self.errorLog("Invalid entry for Effect Intensity - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['effectintensity'] = "Invalid entry for Effect Intensity - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
        #Validate Increase effect intensity
        if 'increaseeffectintensity' in valuesDict:
            try:
                increaseeffectintensity=int(valuesDict['increaseeffectintensity'])
            except:
                self.errorLog("Invalid entry for Increase Effect Intensity - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['increaseeffectintensity'] = "Invalid entry for Increase Effect Intensity - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['increaseeffectintensity']))
            if  not(int(valuesDict['increaseeffectintensity']) in xrange(1,101)):

                self.errorLog("Invalid entry for Increase Effect Intensity - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['increaseeffectintensity'] = "Invalid entry for Increase Effect Intensity - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
        #Validate Decrease effect intensity
        if 'decreaseeffectintensity' in valuesDict:
            try:
                decreaseeffectintensity=int(valuesDict['decreaseeffectintensity'])
            except:
                self.errorLog("Invalid entry for Decrease Effect Intensity - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['decreaseeffectintensity'] = "Invalid entry for  Decrease Effect Intensity - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['decreaseeffectintensity']))
            if  not(int(valuesDict['decreaseeffectintensity']) in xrange(1,101)):

                self.errorLog("Invalid entry for Decrease Effect Intensity - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['decreaseeffectintensity'] = "Invalid entry for Decrease Effect Intensity - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
        #Validate Effect Speed
        if 'effectspeed' in valuesDict:
            try:
                effectspeed=int(valuesDict['effectspeed'])
            except:
                self.errorLog("Invalid entry for Effect Speed - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['effectspeed'] = "Invalid entry for Effect Speed - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['effectspeed']))
            if not(int(valuesDict['effectspeed']) in xrange(0,256)):
                self.errorLog("Invalid entry for Effect Speed - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['effectspeed'] = "Invalid entry for Effect Speed - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
        #Validate Increase effect intensity
        if 'increaseeffectspeed' in valuesDict:
            try:
                increaseeffectspeed=int(valuesDict['increaseeffectspeed'])
            except:
                self.errorLog("Invalid entry for Increase Effect Speed - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['increaseeffectspeed'] = "Invalid entry for Increase Effect Speed - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['increaseeffectspeed']))
            if  not(int(valuesDict['increaseeffectspeed']) in xrange(1,101)):

                self.errorLog("Invalid entry for Increase Effect Speed - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['increaseeffectspeed'] = "Invalid entry for Increase Effect Speed - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
        #Validate Decrease effect speed
        if 'decreaseeffectspeed' in valuesDict:
            try:
                decreaseeffectspeed=int(valuesDict['decreaseeffectspeed'])
            except:
                self.errorLog("Invalid entry for Decrease Effect Speed - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['decreaseeffectspeed'] = "Invalid entry for  Decrease Effect Speed - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['decreaseeffectspeed']))
            if  not(int(valuesDict['decreaseeffectspeed']) in xrange(1,101)):

                self.errorLog("Invalid entry for Decrease Effect speed - must be a whole number between 1 and 100")
                errorsDict = indigo.Dict()
                errorsDict['decreaseeffectspeed'] = "Invalid entry for Decrease Effect Intensity - must be a whole number between 1 and 100"
                return (False, valuesDict, errorsDict)
        #Validate Transition
        if 'transition' in valuesDict:
            try:
                transition=int(valuesDict['transition'])
            except:
                self.errorLog("Invalid entry for Crossfade - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['transition'] = "Invalid entry for Crossfade - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['transition']))
            if not(int(valuesDict['transition']) in xrange(0,256)):
                self.errorLog("Invalid entry for Crossfade - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['transition'] = "Invalid entry for Crossfade - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'preset' in valuesDict:
            try:
                preset=int(valuesDict['preset'])
            except:
                self.errorLog("Invalid entry for Preset - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['transition'] = "Invalid entry for Preset - must be a whole number between -1 and 65535"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['preset']))
            if not(int(valuesDict['preset']) in xrange(-1,65536)):
                self.errorLog("Invalid entry for Preset - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['preset'] = "Invalid entry for Preset - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'primaryblue' in valuesDict:
            try:
                primaryblue=int(valuesDict['primaryblue'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['primaryblue'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['primaryblue']))
            if not(int(valuesDict['primaryblue']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['primaryblue'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'primaryred' in valuesDict:
            try:
                primaryred=int(valuesDict['primaryred'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['primaryred'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['primaryred']))
            if not(int(valuesDict['primaryred']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['primaryred'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'primarygreen' in valuesDict:
            try:
                primarygreen=int(valuesDict['primarygreen'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['primarygreen'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['primarygreen']))
            if not(int(valuesDict['primarygreen']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['primarygreen'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'secondaryblue' in valuesDict:
            try:
                secondaryblue=int(valuesDict['secondaryblue'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['secondaryblue'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['secondaryblue']))
            if not(int(valuesDict['secondaryblue']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['secondaryblue'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'secondaryred' in valuesDict:
            try:
                secondaryred=int(valuesDict['secondaryred'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['secondaryred'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['secondaryred']))
            if not(int(valuesDict['secondaryred']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['secondaryred'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        if 'secondarygreen' in valuesDict:
            try:
                secondarygreen=int(valuesDict['secondarygreen'])
            except:
                self.errorLog("Invalid entry for Colour - must be a whole number between 0 and 255")
                errorsDict = indigo.Dict()
                errorsDict['secondarygreen'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)
            self.debugLog(int(valuesDict['secondarygreen']))
            if not(int(valuesDict['secondarygreen']) in xrange(0,256)):
                self.errorLog("Invalid entry for Colour - must be a whole number between -1 and 65535")
                errorsDict = indigo.Dict()
                errorsDict['secondarygreen'] = "Invalid entry for Colour - must be a whole number between 0 and 255"
                return (False, valuesDict, errorsDict)

        #Otherwise we are all good
        return (True, valuesDict)


    ########################################
    # Menu Methods
    ########################################
    def toggleDebugging(self):
        if self.debug:
            indigo.server.log("Turning off debug logging")
            self.pluginPrefs["showDebugInfo"] = False
        else:
            indigo.server.log("Turning on debug logging")
            self.pluginPrefs["showDebugInfo"] = True
        self.debug = not self.debug

    ########################################
    # Relay / Dimmer Action callback
    ######################
    def actionControlDevice(self, action, dev):
        ###### TURN ON  WLED ######
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            jsondata = json.dumps({ "on": True})
            try:
                wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledonresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                sendSuccess = False

            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s" % (dev.name, "on"))

                # And then tell the Indigo Server to update the state.
                dev.updateStateOnServer("onOffState", True)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s failed" % (dev.name, "on"), isError=True)

        ###### TURN OFF ######
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            # Turn WLED off
            jsondata = json.dumps({ "on": False})
            try:
                wledoffresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledoffresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                        sendSuccess = False

            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s" % (dev.name, "off"))

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("onOffState", False)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s failed" % (dev.name, "off"), isError=True)


        ###### TOGGLE ######
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            # Toggle the WLED
            newOnState = not dev.onState
            jsondata = json.dumps({ "on": newOnState})
            try:
                wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledonresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                sendSuccess = False


            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s" % (dev.name, "toggle"))

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("onOffState", newOnState)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s failed" % (dev.name, "toggle"), isError=True)

        ###### SET BRIGHTNESS ######
        # Implemented for WLED but will be tidied up
        elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
            newBrightness = action.actionValue
            self.debugLog(newBrightness)
            self.debugLog(type(newBrightness))
            adjustedbrightness = int(newBrightness * 2.55)
            self.debugLog(adjustedbrightness)
            self.debugLog(type(adjustedbrightness))
            jsondata = json.dumps({ "bri": adjustedbrightness})
            try:
                wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledonresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s to %d" % (dev.name, "set brightness", newBrightness))

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", newBrightness)
                # Then adjust the raw brightness in the device states (the 0 - 255 value)
                dev.updateStateOnServer("brightness", adjustedbrightness)


            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s to %d failed" % (dev.name, "set brightness", newBrightness), isError=True)

        ###### BRIGHTEN BY ######
        elif action.deviceAction == indigo.kDeviceAction.BrightenBy:
            # Command WLDE hardware module (dev) to do a relative brighten here to be added
            newBrightness = dev.brightness + action.actionValue
            if newBrightness > 100:
                newBrightness = 100
            adjustedbrightness =int(newBrightness * 2.55)
            jsondata = json.dumps({ "bri": adjustedbrightness})
            try:
                wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledonresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                sendSuccess = False

            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s to %d" % (dev.name, "brighten", newBrightness))

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", newBrightness)
                # Then adjust the raw brightness in the device states (the 0 - 255 value)
                dev.updateStateOnServer("brightness", adjustedbrightness)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s to %d failed" % (dev.name, "brighten", newBrightness), isError=True)

        ###### DIM BY ######
        elif action.deviceAction == indigo.kDeviceAction.DimBy:
            # Command WLED to dim by relative amount
            newBrightness = dev.brightness - action.actionValue
            if newBrightness < 0:
                newBrightness = 0
            adjustedbrightness =int(newBrightness * 2.55)
            jsondata = json.dumps({ "bri": adjustedbrightness})
            try:
                wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                if wledonresponse.status_code == 200:
                        sendSuccess = True
                else:
                        sendSuccess = False
            except:
                sendSuccess = False

            if sendSuccess:
                # If success then log that the command was successfully sent.
                indigo.server.log(u"sent \"%s\" %s to %d" % (dev.name, "dim", newBrightness))

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", newBrightness)
                # Then adjust the raw brightness in the device states (the 0 - 255 value)
                dev.updateStateOnServer("brightness", adjustedbrightness)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                indigo.server.log(u"send \"%s\" %s to %d failed" % (dev.name, "dim", newBrightness), isError=True)



    ########################################
    # General Action callback  - for WLED none of these are implemented and some will likely be removed, just left from sample plugin for now
    ######################


        ###### ENERGY UPDATE ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyUpdate:
            # Request hardware module (dev) for its most recent meter data here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "energy update request WLED not Implemented"))

        ###### ENERGY RESET ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyReset:
            # Request that the hardware module (dev) reset its accumulative energy usage data here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "energy reset request WLED not implemented"))

        ###### STATUS REQUEST ######
        elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
            # Query hardware module (dev) for its current status here:
            # ** IMPLEMENT ME **
            indigo.server.log(u"sent \"%s\" %s" % (dev.name, "status request WLED not Implemented"))
    #####
    ## Create the lists for the action menus, this reads the then current effect list dynamically by device so should survive wled upgrades

    # Create the dynamic list for the effects
    def genEffectsList(self, filter, valuesDict, typeId, devID):
        device = indigo.devices[devID]
        theUrl = u"http://"+ device.pluginProps["ipaddress"]+ "/json/eff"
        try:
            effectjson = requests.get(theUrl, timeout=float(self.pluginPrefs["requeststimeout"]))
            effectjson.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.errorLog("HTTP error getting WLED %s effect data: %s" % (device.pluginProps["ipaddress"], str(e)))
            return
        except Exception, e:
            self.errorLog("Unknown error getting WLED effect %s data: %s" % (device.pluginProps["ipaddress"], str(e)))
            return
        effectlist = json.loads(effectjson.text)
        #Update device property so the effect list can be referenced by the set effect method
        newDevProps = device.pluginProps
        newDevProps["wledeffects"]= effectlist
        device.replacePluginPropsOnServer(newDevProps)
        self.debugLog(effectlist)
        return  effectlist

    # Create the dynamic lists for the palettes
    def genPaletteList(self, filter, valuesDict, typeId, devID):
        device = indigo.devices[devID]
        theUrl = u"http://"+ device.pluginProps["ipaddress"]+ "/json/pal"
        try:
            palettejson = requests.get(theUrl, timeout=float(self.pluginPrefs["requeststimeout"]))
            palettejson.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.errorLog("HTTP error getting WLED %s palette data: %s" % (device.pluginProps["ipaddress"], str(e)))
            return
        except Exception, e:
            self.errorLog("Unknown error getting WLED palette %s data: %s" % (device.pluginProps["ipaddress"], str(e)))
            return
        palettelist = json.loads(palettejson.text)
        newDevProps = device.pluginProps
        newDevProps["wledpalettes"]= palettelist
        device.replacePluginPropsOnServer(newDevProps)
        return  palettelist

    ###### SET EFFECT WLED METHOD ######
    def setEffect(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newEffect = pluginAction.props.get("effectdescription")
                effectIndex =dev.pluginProps["wledeffects"].index(newEffect)
                self.debugLog("New Effect is "+newEffect+" with index number "+str(effectIndex))
                jsondata = json.dumps({ "seg":[{"fx":effectIndex}]})
                self.debugLog(jsondata)
                try:
                    wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(wledeffectresponse)
                    if wledeffectresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %d which is %s" % (dev.name, "set effect", effectIndex, newEffect))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effect", effectIndex)
                    dev.updateStateOnServer("effectname", dev.pluginProps["wledeffects"][effectIndex])


    ###### SET EFFECT Intensity WLED METHOD ######
    def setEffectIntensity(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newIntensity = int(pluginAction.props.get("effectintensity"))
                self.debugLog("New Effect Intensity is "+str(newIntensity))
                jsondata = json.dumps({ "seg":[{"ix":newIntensity}]})
                self.debugLog(jsondata)
                try:
                    wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(wledeffectresponse)
                    if wledeffectresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "set effect intensity",  newIntensity))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectintensity", newIntensity)

###### SET EFFECT SPEED WLED METHOD ######
    def setEffectSpeed(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newSpeed = int(pluginAction.props.get("effectspeed"))
                self.debugLog("New Effect Speed is "+str(newSpeed))
                jsondata = json.dumps({ "seg":[{"sx":newSpeed}]})
                self.debugLog(jsondata)
                try:
                    wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(wledeffectresponse)
                    if wledeffectresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "set effect speed",  newSpeed))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectspeed", newSpeed)

###### SET CROSSFADE ######
    def setTransition(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newTransition = int(pluginAction.props.get("transition"))
                self.debugLog("New Crossfade is "+str(newTransition))
                jsondata = json.dumps({ "transition":newTransition})
                self.debugLog(jsondata)
                try:
                    transitionresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(transitionresponse)
                    if transitionresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "set Crossfade",  newTransition))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("transition", newTransition)

    ###### SET PALETTE WLED METHOD ######
    def setEffectPalette(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newPalette = pluginAction.props.get("palettedescription")
                self.debugLog(newPalette)
                paletteIndex =dev.pluginProps["wledpalettes"].index(newPalette)
                self.debugLog("New Palette is "+newPalette+" with index number "+str(paletteIndex))
                jsondata = json.dumps({ "seg":[{"pal":paletteIndex}]})
                self.debugLog(jsondata)
                try:
                    wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(wledeffectresponse)
                    if wledeffectresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %d which is %s" % (dev.name, "set palette", paletteIndex, newPalette))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("palette", paletteIndex)
                    dev.updateStateOnServer("palettename", dev.pluginProps["wledpalettes"][paletteIndex])

    ####### SET Primary RGB WLED Level Method

    def setPrimaryRGB(self, pluginAction, dev):
                self.debugLog(pluginAction)
                red = pluginAction.props.get("primaryred")
                green = pluginAction.props.get("primarygreen")
                blue = pluginAction.props.get("primaryblue")
                jsondata = json.dumps({"seg":[{"col":[[red, green, blue]]}]})
                self.debugLog(jsondata)
                try:
                    rgbresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(rgbresponse)
                    if rgbresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False


                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" Primary R %s  G %s B %s" % (dev.name, red, green, blue))
                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("primaryredvalue", int(red))
                    dev.updateStateOnServer("primarygreenvalue", int(green))
                    dev.updateStateOnServer("primarybluevalue", int(blue))

    ####### SET Secondary RGB WLED Level Method

    def setSecondaryRGB(self, pluginAction, dev):
                self.debugLog(pluginAction)
                red = pluginAction.props.get("secondaryred")
                green = pluginAction.props.get("secondarygreen")
                blue = pluginAction.props.get("secondaryblue")
                jsondata = json.dumps({"seg":[{"col":[[red, green, blue]]}]})
                self.debugLog(jsondata)
                try:
                    rgbresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(rgbresponse)
                    if rgbresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

###### SET PRESET ######
    def setPreset(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newPreset = int(pluginAction.props.get("preset"))
                self.debugLog("New Preset is "+str(newPreset))
                jsondata = json.dumps({ "ps":newPreset})
                self.debugLog(jsondata)
                try:
                    presetresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(presetresponse)
                    if presetresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "set Preset",  newPreset))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("preset", newPreset)

###### Increase Effect Intensity by % ######
    def increaseEffectIntensity(self, pluginAction, dev):
                self.debugLog(pluginAction)
                neweffectintensity = int(dev.states["effectintensity"] + (int(pluginAction.props.get("increaseeffectintensity")) *2.55))
                if neweffectintensity > 255:
                	neweffectintensity = 255
                self.debugLog("New Increased Effect Intensity "+str(neweffectintensity))
                jsondata = json.dumps({ "seg":[{"ix":neweffectintensity}]})
                self.debugLog(jsondata)
                try:
                    increaseresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(increaseresponse)
                    if increaseresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Increased effect intensity by percentage to",  neweffectintensity))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectintensity", neweffectintensity)

###### Decrease Effect Intensity by % ######
    def decreaseEffectIntensity(self, pluginAction, dev):
                self.debugLog(pluginAction)
                neweffectintensity = int(dev.states["effectintensity"] - (int(pluginAction.props.get("decreaseeffectintensity")) *2.55))
                if neweffectintensity < 0:
                	neweffectintensity = 0
                self.debugLog("New Decreased Effect Intensity "+str(neweffectintensity))
                jsondata = json.dumps({ "seg":[{"ix":neweffectintensity}]})
                self.debugLog(jsondata)
                try:
                    decreaseresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(decreaseresponse)
                    if decreaseresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Decreased effect intensity by percentage to",  neweffectintensity))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectintensity", neweffectintensity)

###### Increase Effect Speed by % ######
    def increaseEffectSpeed(self, pluginAction, dev):
                self.debugLog(pluginAction)
                neweffectspeed = int(dev.states["effectspeed"] + (int(pluginAction.props.get("increaseeffectspeed")) *2.55))
                if neweffectspeed > 255:
                	neweffectspeed = 255
                self.debugLog("New Increased Effect Speed "+str(neweffectspeed))
                jsondata = json.dumps({ "seg":[{"sx":neweffectspeed}]})
                self.debugLog(jsondata)
                try:
                    increaseresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(increaseresponse)
                    if increaseresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Increased effect speed by percentage to",  neweffectspeed))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectspeed", neweffectspeed)

###### Decrease Effect Intensity by % ######
    def decreaseEffectSpeed(self, pluginAction, dev):
                self.debugLog(pluginAction)
                neweffectspeed = int(dev.states["effectspeed"] - (int(pluginAction.props.get("decreaseeffectspeed")) *2.55))
                if neweffectspeed < 0:
                	neweffectspeed = 0
                self.debugLog("New Decreased Effect Speed "+str(neweffectspeed))
                jsondata = json.dumps({ "seg":[{"sx":neweffectspeed}]})
                self.debugLog(jsondata)
                try:
                    decreaseresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(decreaseresponse)
                    if decreaseresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Decreased effect speed by percentage to",  neweffectspeed))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("effectspeed", neweffectspeed)
###### Set to UDP Send ######
    def setUDPsend(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newsetUDPsend = pluginAction.props.get("UDPsend")
                self.debugLog("Sync to UDP Send set to "+str(newsetUDPsend))
                jsondata = json.dumps({ "udpn":{"send":newsetUDPsend}})
                self.debugLog(jsondata)
                try:
                    setudpresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(setudpresponse)
                    if setudpresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Set UDPsend",  newsetUDPsend))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("UDPsend", newsetUDPsend)

###### Set to UDP Receive ######
    def setUDPrecv(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newsetUDPrecv = pluginAction.props.get("UDPrecv")
                self.debugLog("UDP Receive set to "+str(newsetUDPrecv))
                jsondata = json.dumps({ "udpn":{"recv":newsetUDPrecv}})
                self.debugLog(jsondata)
                try:
                    setudpresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(setudpresponse)
                    if setudpresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Set UDPrecv",  newsetUDPrecv))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("UDPrecv", newsetUDPrecv)

###### Set to Sync Preset ######
    def setCycle(self, pluginAction, dev):
                self.debugLog(pluginAction)
                newsetCycleBoolean = pluginAction.props.get("PresetCycle")
                if newsetCycleBoolean :
                	newsetCycle = "0"
                else:
                	newsetCycle = "-1"        	
                self.debugLog("Cycle set to "+str(newsetCycle))
                jsondata = json.dumps({ "pl":newsetCycle})
                self.debugLog(jsondata)
                try:
                    setudpresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=float(self.pluginPrefs["requeststimeout"]))
                    self.debugLog(setudpresponse)
                    if setudpresponse.status_code == 200:
                            sendSuccess = True
                    else:
                            sendSuccess = False
                except:
                    sendSuccess = False

#			sendSuccess = True		# Set to False if it failed.

                if sendSuccess:
                # If success then log that the command was successfully sent.
                    indigo.server.log(u"sent \"%s\" %s to %s " % (dev.name, "Set Cycle",  newsetCycle))

                    # And then tell the Indigo Server to update the state:
                    dev.updateStateOnServer("preset", newsetCycle)

