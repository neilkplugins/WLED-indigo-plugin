# WLED-indigo-plugin
This Indigo Plugin supports the excellent WLED software from http:://wled.me

This initial version should be considered very much "Alpha", and used only if you don't mind finding issues, and reporting them to me to fix whenever I find time.  Check the Wiki out for detailed instructions on usage 

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address and this currently has no validation or error checking
2) Master Strip/String Power on, and off
3) WLED States that are reflected in the device are by default currently polled every 60s (this can be configured in the plugin configuration).  I have not mapped everything but the things that make sense are done.  I have focussed more on the plugin than WLED functionality at this stage so feel free to ask if I missed something useful.  
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness, as well as "Dim by", "Brighten by" and "Toggle" universal actions.
5) I have implemented the most important of the effect and palette related options, including Effect, Palette, Speed, Itensity and Transition.  I will investigate what if any support for macros makes sense.
6) The Primary and Secondary RGB colours can be set by two respective actions, and the effects that use them as a base will work the same as via the app.  Presets can also be recalled.
7) Please suggest anything else that you think would be useful, I will take a look
8) The states currently defined should now be stable, and not require re-saving the device properties between versions.  I cannot promise but I have walked through the API and picked the things that are likely be used.  I also added software version and freeheap in case this helps us identify issues (and elegantly handle new WLED versions)
I have had limited opportunity to test, nothing should cause any issues however it is possible I have missed some really basic functionality and not caught the omission, so try at this stage at your own risk.   Also I have implemented very little error handling, this will come when I have base functionality done and before I suggest publishing in the Indigo Store.  I now also have a sub forum for the WLED plugin on the Indigo forum. 

Cautions:

I am not an expert on WLED and the test usage is a single strip. I have not as yet considered any kind of throttling of API requests. We just need to do some more real world testing.  For now I am just relying on polling frequency changes via the overall plugin configuration (Plugins-WLED-Configure) and timeout configuration for the JSON API requests. I notice the timeout period may need to increase if the WLED throws errors in the Indigo log.

PLEASE BE AWARE You may need to open and resave the device configuration as I add additional states, this will also impact actions, schedules that reference the device.  Do this if you get an error like
"Error device "WLED1" state key primarybluevalue not defined (ignoring update request)"
then opening and resaving the configuration should resolve it.

As this is an Alpha version, I have not had a chance to test as comprehensively as I would like.  By using this version you are joining my virtual testing team, welcome on board and thanks for the help !
