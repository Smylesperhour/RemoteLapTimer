import os
os.system("sudo iwconfig wlan0 power off")
os.system("sudo dhclient wlan0")
