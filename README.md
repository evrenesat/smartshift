SmartShift
==========
SmartShift is a Python script for changing brightness and color temperature of screen. 
It uses ;
- redshift for setting brigthness and color temprature (it working for any lcd monitor, not just notebooks which has an acpi brigthness setting)
- gstreamer for taking periodic shots from webcam to determine ambient illumination.
- python-xlib to catch window switch events.
- python-xlib or xprop to get the name of active window.

