#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import math
import configparser
import sys
import pickle

def flash(N):
    j = 0
    while j <= N:
        GPIO.output(light, 1)
        time.sleep(.25)
        GPIO.output(light, 0)
        time.sleep(.25)
        j = j + 1

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def check_wifi():

    if "Snocam_Hub" in os.popen(iwlist).read():
        status = "Connected"
        net_status = os.popen(net_cfg).read()
        if ".Snocam" in net_status:
            os.system(ifswitch)
        else:
            print("You have Snocams!")

    else:
        print("No WIFI found.")
        status = "Not Connected"

    print(status)
    return status

def kill_sampling(scriptNames):

    for script in scriptNames:
        os.system("sudo pkill -9 -f {}".format(script))

def update_time():
    try:
        samp_time = os.popen("sudo hwclock -u -r").read()
        samp_time = samp_time.split('.',1)[0]
        samp_time = samp_time.replace("  ","_")
        samp_time = samp_time.replace(" ","_")
        samp_time = samp_time.replace(":","-")

        firstp = open("/home/pi/Documents/Snocam_scripts/timesamp.pkl","wb")
        pickle.dump(samp_time, firstp)
        firstp.close()
    except:
        print("update time failed")

update_time()

i = 0
light = 12
wifi = 7
Press_IO = 11
BURN = 33

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(light, GPIO.OUT)
GPIO.setup(wifi, GPIO.OUT)
GPIO.setup(Press_IO, GPIO.OUT)
GPIO.output(Press_IO, 1)
GPIO.output(wifi, 1)

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Snocam_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Snocam_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)

driveSize = float(config['Flash_Drive_Size']['GB'])

iniImg = str2bool(config['Sampling_scripts']['Image'])
iniTpp = str2bool(config['Sampling_scripts']['TempPres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

### Drive size conversion ### ~3 MB cycle, 4GB extra space reserved on disk

TotalSamples = ((driveSize - 4)*300)

print("Total Possible Samples {}".format(TotalSamples))

ifswitch = "sudo python /home/pi/Documents/Snocam_tools/dhcp-switch.py"

iwlist = 'sudo iwlist wlan0 scan | grep "Snocam_Hub"'

net_cfg = "ls /etc/ | grep dhcp"

ping_hub = "ping 192.168.0.1 -c 1"

ping_google = "ping google.com -c 1"

ps_test = "pgrep -a python"

scriptNames = ["Temp.py", "TempPres.py", "Snocam_image.py","OXYBASE_RS232.py","ACC_100Hz.py","Extended_Sampler.py","Snocam_image_IF.py","TempPres_IF.py","OXYBASE_RS232_IF.py","ACC_100Hz_IF.py"]

if __name__ == '__main__':

    if len(os.listdir('{}/Snocam_pics'.format(configDir))) >= TotalSamples or len(os.listdir('{}/Snocam_data'.format(configDir))) >= TotalSamples:

        print("You have reached the data limit")
        flash(5)

    else:

        if iniTpp == True:
            os.system('sudo python /home/pi/Documents/Snocam_scripts/TempPres.py &')

        if iniImg == True:
            os.system('sudo python /home/pi/Documents/Snocam_scripts/Snocam_image.py &')

        if iniO2 == True:
            os.system('sudo python /home/pi/Documents/Snocam_scripts/OXYBASE_RS232.py &')

        if iniAcc == True:
            os.system('sudo python /home/pi/Documents/Snocam_scripts/ACC_100Hz.py &')

    time.sleep(5)

    while(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:

    ## Check for wifi

        if check_wifi() == "Connected":
            flash(2)
            kill_sampling(scriptNames)
            exit(0)

        else:
            print("Sampling")
            time.sleep(Stime*30)

    print('Goodbye')
    GPIO.output(wifi, 0)
    time.sleep(5)
    os.system('sudo shutdown now')
