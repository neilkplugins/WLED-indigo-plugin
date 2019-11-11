#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2019 neilk
# 
# Based on a hacked around sample dimmer plugin

################################################################################
# Imports
################################################################################
import indigo
import requests
import urllib2
import json

################################################################################
# Globals
################################################################################
theUrlBase = u"/json"
#TODO get these lists by device and build dynamically as potentially future versions will break this and changes to effects will need manual updates, used in the genEffectsList and Effects methods		
wledeffects = [u'Solid', u'Blink', u'Breathe', u'Wipe', u'Wipe Random', u'Random Colors', u'Sweep', u'Dynamic', u'Colorloop', u'Rainbow', u'Scan', u'Dual Scan', u'Fade', u'Chase', u'Chase Rainbow', u'Running', u'Saw', u'Twinkle', u'Dissolve', u'Dissolve Rnd', u'Sparkle', u'Dark Sparkle', u'Sparkle+', u'Strobe', u'Strobe Rainbow', u'Mega Strobe', u'Blink Rainbow', u'Android', u'Chase', u'Chase Random', u'Chase Rainbow', u'Chase Flash', u'Chase Flash Rnd', u'Rainbow Runner', u'Colorful', u'Traffic Light', u'Sweep Random', u'Running 2', u'Red & Blue', u'Stream', u'Scanner', u'Lighthouse', u'Fireworks', u'Rain', u'Merry Christmas', u'Fire Flicker', u'Gradient', u'Loading', u'In Out', u'In In', u'Out Out', u'Out In', u'Circus', u'Halloween', u'Tri Chase', u'Tri Wipe', u'Tri Fade', u'Lightning', u'ICU', u'Multi Comet', u'Dual Scanner', u'Stream 2', u'Oscillate', u'Pride 2015',u'Juggle', u'Palette', u'Fire 2012', u'Colorwaves', u'BPM', u'Fill Noise', u'Noise 1', u'Noise 2', u'Noise 3', u'Noise 4', u'Colortwinkles', u'Lake', u'Meteor', u'Smooth Meteor', u'Railway', u'Ripple', u'Twinklefox', u'Twinklecat', u'Halloween Eyes']
wledpalettes = [u'Default', u'Random Cycle', u'Primary Color', u'Based on Primary', u'Set Colors', u'Based on Set', u'Party', u'Cloud', u'Lava', u'Ocean', u'Forest', u'Rainbow', u'Rainbow Bands', u'Sunset', u'Rivendell', u'Breeze', u'Red & Blue', u'Yellowout', u'Analogous', u'Splash', u'Pastel', u'Sunset 2', u'Beech', u'Vintage', u'Departure', u'Landscape', u'Beach', u'Sherbet', u'Hult', u'Hult 64', u'Drywet', u'Jul', u'Grintage', u'Rewhi', u'Tertiary', u'Fire', u'Icefire', u'Cyane', u'Light Pink', u'Autumn', u'Magenta', u'Magred', u'Yelmag', u'Yelblu', u'Orange & Teal', u'Tiamat', u'April Night', u'Orangery', u'C9', u'Sakura']



######################################## Do I need or use this ??
def updateVar(name, value, folder=0):
	if name not in indigo.variables:
		indigo.variable.create(name, value=value, folder=folder)
	else:
		indigo.variable.updateValue(name, value)

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
		try:
			while True:
				# we sleep (1 minutes) first because when the plugin starts, each device
				# is updated as they are started.
				# This will be configurable in a future version, for now just change the number of seconds in the line below
				self.sleep(1 * int(self.pluginPrefs["pollingFrequency"]) )
				# now we cycle through each WLED
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
		except self.StopThread:
			pass

	########################################
	def update(self,device):
		self.debugLog("Updating device: " + device.name)
		theUrl = u"http://"+ device.pluginProps["ipaddress"]+ "/json"
		try:
			f = urllib2.urlopen(theUrl, timeout=1)
		except urllib2.HTTPError, e:
			self.errorLog("HTTP error getting WLED %s data: %s" % (device.pluginProps["ipaddress"], str(e)))
			return
		except Exception, e:
			self.errorLog("Unknown error getting WLED %s data: %s" % (device.pluginProps["ipaddress"], str(e)))
			return
		#Get the JSON from the WLED to update device states
		statusjson = json.load(urllib2.urlopen(theUrl,timeout=1))
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


		
		


	########################################
	# UI Validate, Close, and Actions defined in Actions.xml:
	########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		wledIP = valuesDict['ipaddress'].encode('ascii','ignore').upper()
		valuesDict['ipaddress'] = wledIP
		theUrl = u"http://"+ wledIP+ theUrlBase
		try:
			urllib2.urlopen(theUrl,timeout=1)
		except urllib2.HTTPError, e:
			errorsDict = indigo.Dict()
			errorsDict['ipaddress'] = "WLED not found or isn't responding"
			self.errorLog("Error getting WLED data: %s" % wledIP)
			return (False, valuesDict, errorsDict)

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
				wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				wledoffresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				wledonresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
	## Create the lists for the action menus, need to make this 		
	
	def genEffectsList(self, filter="", valuesDict=None, typeId="",targetId=0):
		#TODO make this really dynamic by looking up by device. shouldn't be an issue if all wleds are on the same version, currently just refers to global variable
		return  wledeffects
	
	def genPaletteList(self, filter="", valuesDict=None, typeId="",targetId=0):
		#TODO make this really dynamic by looking up by device. shouldn't be an issue if all wleds are on the same version, currently just refers to global variable
		return  wledpalettes
	
	###### SET EFFECT WLED METHOD ######
	def setEffect(self, pluginAction, dev):
				self.debugLog(pluginAction)
				newEffect = pluginAction.props.get("effectdescription")
				effectIndex =wledeffects.index(newEffect)
				self.debugLog("New Effect is "+newEffect+" with index number "+str(effectIndex))
				jsondata = json.dumps({ "seg":[{"fx":effectIndex}]})
				self.debugLog(jsondata)
				try:
					wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
					dev.updateStateOnServer("effectname", wledeffects[effectIndex])


	###### SET EFFECT Intensity WLED METHOD ######
	def setEffectIntensity(self, pluginAction, dev):
				self.debugLog(pluginAction)
				newIntensity = int(pluginAction.props.get("effectintensity"))
				self.debugLog("New Effect Intensity is "+str(newIntensity))
				jsondata = json.dumps({ "seg":[{"sx":str(newIntensity)}]})
				self.debugLog(jsondata)
				try:
					wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
				jsondata = json.dumps({ "seg":[{"ix":str(newSpeed)}]})
				self.debugLog(jsondata)
				try:
					wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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


	###### SET PALETTE WLED METHOD ######
	def setEffectPalette(self, pluginAction, dev):
				self.debugLog(pluginAction)
				newPalette = pluginAction.props.get("palettedescription")
				self.debugLog(newPalette)
				paletteIndex =wledpalettes.index(newPalette)
				self.debugLog("New Palette is "+newPalette+" with index number "+str(paletteIndex))
				jsondata = json.dumps({ "seg":[{"pal":paletteIndex}]})
				self.debugLog(jsondata)
				try:
					wledeffectresponse = requests.post('http://'+ dev.pluginProps["ipaddress"] + theUrlBase,data=jsondata,timeout=1)
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
					indigo.server.log(u"sent \"%s\" %s to %d which is %s" % (dev.name, "set effect", paletteIndex, newPalette[0]))

					# And then tell the Indigo Server to update the state:
					dev.updateStateOnServer("palette", paletteIndex)
					dev.updateStateOnServer("palettename", wledpalettes[paletteIndex])

