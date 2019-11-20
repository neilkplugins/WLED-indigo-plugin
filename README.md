## WLED-indigo-plugin
This Indigo Plugin provides support for the excellent WLED software from [the WLED GitHub](http:://wled.me) by Aircookie for the also excellent [Indigo Domotics Software ](http://www.indigodomo.com)

### What is WLED?

WLED is a software package written for the NodeMCU microcontroller, designed to control individually addressable LED Strings/Strips written by AirCookie. I have informed the developer and he is happy to see support for more applications. The WLED software is really powerful, and has an associated mobile APP as well as extensive API's that the plugin exploits. It is an impressive piece of work on a very low cost hardware platform.

You will find the WLED details at http://wled.me with instructions on how to download and flash your NodeMCU. Also an excellent  [video](https://www.youtube.com/watch?v=tXvtxwK3jRk) which covers all you need to know to get the strip up and running. Finally this [video](https://www.youtube.com/watch?v=6eCE2BpLaUQ)  covers the usage of the WLED controller in great detail.

### The WLED Plugin

The plugin is based on the Indigo Dimmer device. Each WLED device has a unique IP address, and you can add as many as you need.

This initial version has been tested by myself and forum user Seeker.  It is my first plugin and foray into python, I will endeavour to address any issues you find as time permits. Check the Wiki out for detailed instructions on usage [on the GitHub Wiki](https://github.com/neilkplugins/WLED-indigo-plugin/wiki)

The plugin currently supports :-

1) Creation of Multiple WLED Devices, the only device property is the WLED IP Address.
2) Master Strip/String Power on, and off
3) WLED States that are reflected in the device are by default polled every 60s (this can be configured in the plugin configuration).   
4) The Indigo Dimmer device, and "Set Brightness" actions control the master WLED brightness, as well as "Dim by", "Brighten by" and "Toggle" actions.
5) I have implemented the most important of the effect and palette related options, including Effect, Palette, Speed, Intensity and Transition.  I will investigate what if any support for macros makes sense for a future version.
6) The Primary and Secondary RGB colours can be set by two respective actions, and the effects that use them as a base will work the same as via the app.
7) Presets can be recalled by an action which may be a good way to address issues that would require multiple actions otherwise.
8) Some device states are for information only, or for future functionality (Night Light if anyone wants it, as you could do the same in Indigo) as well as WLED information like freeheap memory.
9) You can submit support requests, feature requests, feedback or anything else to the  [plugin forum](https://forums.indigodomo.com/viewforum.php?f=319)

### Cautions:

I am not an expert on WLED and the test usage is a single strip.  I have not tested this with large LED numbers, or with some of the more advanced WLED functionality.


As this is the first version of my first plugin, so usage is at your own risk ! By using this version you are joining my virtual testing team, welcome on board and thanks for the help !  I would love to hear your feedback and thoughts.

### Thanks

Thanks for the inspiration and support from the Indigo Community, I would not have been able to complete this without the help I received. You can submit support requests, feature requests, feedback or anything else to the plugin forum  https://forums.indigodomo.com/viewforum.php?f=319

# Cautions:

I am not an expert on WLED and the test usage is a single strip.  I have not tested this with large LED numbers, or with some of the more advanced WLED functionality.


As this is the first version of my first plugin, so usage is at your own risk ! By using this version you are joining my virtual testing team, welcome on board and thanks for the help !  I would love to hear your feedback and thoughts.

# Thanks

Thanks for the inspiration and support from the Indigo Community, I would not have been able to complete this without the help.  
