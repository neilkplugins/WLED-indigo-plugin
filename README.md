# WLED-indigo-plugin
This Indigo Plugin supports the WLED software from http:://wled.me

This initial version should be considered very much "Alpha"

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address and this currently has no validtation or error checking
2) Master Strip Power on, and off
3) WLED States are reflected in the device, currently polled every 60s (this will be configurable when I get around to it).  I have not mapped everyhting but it should be simple to add things you need.  I have focussed more on the plugin than WLED functionality at this stage so feel free to ask if I missed something useful.  I also don't want to drown the NodeMCU with requests, so it is a balance.  You can adjust in the plugin code for now if you want to experiment
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness.  (currently the relative dim by x% function is not implemented)

I have had limited opportunity to test, nothing should cause any issues however it is possible I have missed some really basic functionality and not caught the omission, so try at this stage at your own risk
