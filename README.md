# WLED-indigo-plugin
This Indigo Plugin supports the WLED software from http:://wled.me

This initial version should be considered very much "Alpha", and used only if you don't mind finding issues as you will, and reporting them to me to fix whenever I find time.

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address and this currently has no validtation or error checking
2) Master Strip Power on, and off
3) WLED States that are reflected in the device are by default currently polled every 60s (this can be configured in the plugin configuration).  I have not mapped everyhting but it should be simple to add things you need.  I have focussed more on the plugin than WLED functionality at this stage so feel free to ask if I missed something useful.  I also don't want to drown the NodeMCU with requests, so it is a balance.  You can adjust in the plugin code for now if you want to experiment
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness.
5) I have implemented three effect related actions, allowing you to set an effect type, speed and intensity.  Other actions will be added pretty frequently.
6) My intent was to make the primary RGB settings controllable in the indigo device as well as by action, but it seems more elegant to have the master dimmer mapped to the Indigo Dimmer device. I have added RGB states for the primary and secondary effect colours, but only the primary's update right now (until I figure out the JSON).  Actions will be added to set both colours.
7) I will add actions over time for the remaining items you can set via the API, I have it largely figured out, it is just time.
I have had limited opportunity to test, nothing should cause any issues however it is possible I have missed some really basic functionality and not caught the omission, so try at this stage at your own risk.  You may see functions (like energy usage) and other that look like they work. but may not.  They are hangovers from the sample plugins, and I may do some things with them, or more likely remove if they make no sense for WLED.  Also I have implemented very little error handling, this will come when I have base functionality done and before I suggest published in the Indigo Store.  I have also requested a sub forum for the WLED plugin on the Indigo forum. 

Cautions:

I am not an expert on WLED and the test usage is a single strip. I have not as yet considered any kind of throttling of API requests, and this initial version hits both JSON and XML api's so it does double up a bit. We just need to do some more real world testing.  For now I am just relying on polling frequency changes via the overall plugin configuration (Plugins-WLED-Configure)

PLEASE BE AWARE You may need to delete and re-create devices as I add additional states, this will also impacy actions, schedules that reference the device, so don't invest too much time and effort in that until we are closer to a beta release.
