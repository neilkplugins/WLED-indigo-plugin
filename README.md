# WLED-indigo-plugin
This Indigo Plugin supports the WLED software from http:://wled.me

This initial version should be considered very much "Alpha"

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address and this currently has no validtation or error checking
2) Master Strip Power on, and off
3) WLED States are reflected in the device, currently polled every 60s (this will be configurable when I get around to it).  I have not mapped everyhting but it should be simple to add things you need.  I have focussed more on the plugin than WLED functionality at this stage so feel free to ask if I missed something useful.  I also don't want to drown the NodeMCU with requests, so it is a balance.  You can adjust in the plugin code for now if you want to experiment
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness.
5) You can select the "effect" from a pull down in the set effect options.  I will be adding palette, speed and intensity actions.
6) My intent is to make the primary RGB settings (in fact it is part implemented) controllable in the indigo device as well as by action
7) I will add actions over time for the remaining items you can set via the API, I have it largely figured out, it is just time.
I have had limited opportunity to test, nothing should cause any issues however it is possible I have missed some really basic functionality and not caught the omission, so try at this stage at your own risk.  You may see functions (like energy usage) and other that look like they work. but may not.  They are hangovers from the sample plugins, and I may do some things with them, or more likely remove if they make no sense for WLED.

Cautions:

I am not an expert on WLED and the test usage is a single strip. I have not as yet considered any kind of throttling of API requests, and this initial version hits both JSON and XML api's so it does double up a bit. We just need to do some more real world testing.
