# WLED-indigo-plugin
This Indigo Plugin supports the excellent WLED software from http:://wled.me

This initial version should be considered "Beta", and used only if you don't mind finding issues, and reporting them to me to fix whenever I find time. The prior alpha versions have been tested by end users. Check the Wiki out for detailed instructions on usage https://github.com/neilkplugins/WLED-indigo-plugin/wiki

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address and this currently has no validation or error checking
2) Master Strip/String Power on, and off
3) WLED States that are reflected in the device are by default polled every 60s (this can be configured in the plugin configuration).   I have focussed more on the plugin than WLED functionality at this stage so feel free to ask if I missed something useful.  
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness, as well as "Dim by", "Brighten by" and "Toggle" universal actions.
5) I have implemented the most important of the effect and palette related options, including Effect, Palette, Speed, Intensity and Transition.  I will investigate what if any support for macros makes sense for a future version.
6) The Primary and Secondary RGB colours can be set by two respective actions, and the effects that use them as a base will work the same as via the app.  Presets can also be recalled.
7) Please suggest anything else that you think would be useful, I will take a look
8) The states currently defined are now be stable, and not require re-saving the device properties between versions.    I also added software version and freeheap in case this helps us identify issues (and elegantly handle new WLED versions)
I have had limited opportunity to test, nothing should cause any issues however it is possible I have missed some really basic functionality and not caught the omission, so try at this stage at your own risk.   All configuration options in the plugin have full validation, this does require testing before promotion to the plugin store.  I now also have a sub forum for the WLED plugin on the Indigo forum. 

# Cautions:

I am not an expert on WLED and the test usage is a single strip. I have not as yet considered any kind of throttling of API requests. We just need to do some more real world testing.  For now I am just relying on polling frequency changes via the overall plugin configuration (Plugins-WLED-Configure) and timeout configuration for the JSON API requests. I notice the timeout period may need to increase if the WLED throws errors in the Indigo log.


As this is a Beta version (or maybe v1.0 in the store soon), I have not had a chance to test as comprehensively as I would like.  By using this version you are joining my virtual testing team, welcome on board and thanks for the help !
