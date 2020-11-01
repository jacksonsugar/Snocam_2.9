#!/usr/bin/env python

'''
This program was written to simplify configuration of a
Snocam camera/sensor/vehicle.

More tools to be added in future versions

'''
import RPi.GPIO as GPIO
import time
import os

print "Welcome to the Snocam installer! \n"

ini_dir = os.getcwd()

def yes_no(answer):
    yes = set(['yes','y', 'ye', 'yeet', ''])
    no = set(['no','n'])

    while True:
        choice = raw_input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'\n")

def USB_Conf():

    drive = raw_input('Please insert USB storage device and press return:')
    # Below formats the Drive automatically but wow it's slow
    #os.system('sudo mkfs -t ntfs /dev/sda1')

    drives = os.popen("sudo blkid").read()

    drives = drives.splitlines()

    not_drive = []

    for i in [i for i,x in enumerate(drives) if x.find('mmc') != -1]:
        not_drive.append(i)

    for i in [i for i,x in enumerate(drives) if x.find('loop') != -1]:
        not_drive.append(i)

    drives = [i for j, i in enumerate(drives) if j not in not_drive]

    drive = drives[0]

    drive = drive.split(':')[0]

    print(drive)

    UUID = os.popen('sudo blkid -o value /dev/sda1').read().splitlines()[3]

    print(UUID)

    return UUID

# Configure the last 3 digits of IP 192.168.0.XXX

IP_addr = input('What local IP extension would you like to use? 192.168.0.')

if len(str(IP_addr)) > 3 or len(str(IP_addr)) < 1 or IP_addr <= 1 or IP_addr >= 255:
    IP_fail = 1
    while IP_fail == 1: 
        IP_addr = input('Illigal IP address: 192.168.0.%s! Please try again: ' % IP_addr)
        if len(str(IP_addr)) > 3 or len(str(IP_addr)) < 1 or IP_addr <= 1 or IP_addr >= 255:
            pass
        else:
            IP_fail = 0
            print("Local IP address = 192.168.0.%s" % IP_addr)
else:
    print("Snocam_Hub IP address = 192.168.0.%s" % IP_addr)

# Write to /etc/dhcpcd.Snocam file

os.system('sudo cp source/dhcp/dhcpcd.conf source/dhcp/dhcpcd.Snocam /etc/')

# Open dhcpcd.Snocam
with open('/etc/dhcpcd.Snocam', 'r') as file :
    Snocam_dhcp = file.read()

# Replace the IP string
Snocam_dhcp = Snocam_dhcp.replace('XXX', str(IP_addr))

# Write the file out again
with open('/etc/dhcpcd.Snocam', 'w') as file:
    file.write(Snocam_dhcp)
  
# Set up wifi

os.system("sudo sh -c 'cat source/dhcp/wpa_supplicant.txt >> /etc/wpa_supplicant/wpa_supplicant.conf'")

# Enable the splash screen easter egg
    
Debug = yes_no('Do you want to enable debug mode? [Y/N] : ')

os.system('sudo mv /usr/share/plymouth/themes/pix/splash.png /usr/share/plymouth/themes/pix/splash.png.old')
os.system('sudo cp source/splash.png /usr/share/plymouth/themes/pix/')

if Debug == True:
    os.system("sudo raspi-config nonint do_boot_splash 1")
elif Debug == False:
    os.system("sudo raspi-config nonint do_boot_splash 0")
else:
    print("WTH did you do??")

USBdata = yes_no('Do you wish to configure a USB storage device? (NTFS file system) [Y/N]: ')
os.system('sudo mkdir /home/pi/Documents/Snocam_scripts /home/pi/Documents/Snocam_tools')
# Move the deployment handler so it knows where to look for config file
os.system('sudo cp source/Data_config.ini source/Snocam_DeploymentHandler.py source/Snocam_image.py source/Extended_Sampler.py source/OXYBASE_RS232.py source/TempPres.py source/ACC_100Hz.py source/ACC_100Hz_IF.py source/TempPres_IF.py source/Snocam_image_IF.py source/OXYBASE_RS232_IF.py /home/pi/Documents/Snocam_scripts')

if USBdata == True:

    # Mount SD card for use
    os.system("sudo mkdir /media/Data")

    UUID = USB_Conf()

    print(UUID)

    while UUID != os.popen('sudo blkid -o value /dev/sda1').read().splitlines()[3]:
        USB_Conf()

    os.system("sudo sed -i -e '$a PARTUUID=%s /media/Data      ntfs   defaults  0  0' /etc/fstab" % UUID)

    os.system('sudo mount -a')

    print("All files for operation found inside /media/Data on USB drive!")
    
    time.sleep(3)

    os.system('sudo mkdir /media/Data/Snocam_pics /media/Data/Snocam_data')
    os.system('sudo mkdir /media/Data/Snocam_data/INI /media/Data/Snocam_data/FIN')

    os.system('sudo cp source/Snocam_config.ini /media/Data/')

    os.system("echo '# Snocam IP:192.168.0.{}' >> /media/Data/Snocam_config.ini".format(IP_addr))

    # Open Snocam config file
    with open('/home/pi/Documents/Snocam_scripts/Data_config.ini', 'r') as file :
        Snocam_conf = file.read()

    # Replace the directory
    Snocam_conf = Snocam_conf.replace('/home/pi/Desktop', '/media/Data')

    # Write the file out again
    with open('/home/pi/Documents/Snocam_scripts/Data_config.ini', 'w') as file:
        file.write(Snocam_conf)

elif USBdata == False:

    print("All files for operation found inside /home/pi/Desktop!")
    os.system('sudo mkdir /home/pi/Desktop/Snocam_pics /home/pi/Desktop/Snocam_data')
    os.system('sudo mkdir  /home/pi/Desktop/Snocam_data/INI /home/pi/Desktop/Snocam_data/FIN')
    os.system('sudo cp source/Snocam_config.ini /home/pi/Desktop')
    time.sleep(3)
    os.system("echo '# Snocam IP:192.168.0.{}' >> /home/pi/Desktop/Snocam_config.ini".format(IP_addr))


else:

    print('How did you do this..')

# Set up external software and raspi-config
# Get updates
#os.system('sudo apt-get update && sudo apt-get upgrade -y') 
# Get needed packages
os.system('sudo apt-get install build-essential python-smbus i2c-tools avrdude -y')
# raspi-config
#os.system('sudo raspi-config nonint do_change_locale en_IS.UTF-8')
os.system('sudo raspi-config nonint do_boot_behaviour B2')
os.system('sudo raspi-config nonint do_camera 0')
os.system('sudo raspi-config nonint do_ssh 0')
os.system('sudo raspi-config nonint do_i2c 0')
os.system('sudo raspi-config nonint do_rgpio 0')
# Add alias list to .bashrc
os.system('sudo cat source/Snocam_alias.txt >> /home/pi/.bashrc')
# Clone repos
os.chdir('source/drivers/')
os.system('git clone https://github.com/bluerobotics/tsys01-python.git')
os.system('git clone https://github.com/bluerobotics/ms5837-python.git')
os.system('git clone https://github.com/adafruit/Adafruit_Python_ADXL345.git')
os.system('git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git')
# Install acc driver
os.chdir('Adafruit_Python_ADXL345/')
os.system('sudo python setup.py install')
os.chdir('..')
# Install adc driver
os.chdir('Adafruit_Python_ADS1x15/')
os.system('sudo python setup.py install')
os.chdir('..')

os.system('sudo cp /home/pi/Snocam/source/drivers/ms5837-python/ms5837.py /home/pi/Documents/Snocam_scripts/')
os.system('sudo cp -r /home/pi/Snocam/source/drivers/tsys01-python/tsys01 /home/pi/Documents/Snocam_scripts/')
# Exit
os.chdir(ini_dir)

# Set up and sync RTC
print("Appending /boot/config.txt")
os.system("echo 'dtoverlay=i2c-rtc,ds3231' >> /boot/config.txt")
os.system("echo 'enable_uart=1' >> /boot/config.txt")

# Move scripts to local build
os.system('sudo cp source/Keep_Me_Alive.py source/dhcp-configure.py source/dhcp-switch.py source/RTC_Finish.py source/RTC-set.py source/Shutdown.py source/flasher.py source/Iridium_gps.py source/FishTag_data.py /home/pi/Documents/Snocam_tools/')
os.system('sudo cp -r source/drivers/tsys01-python/tsys01 source/drivers/ms5837-python/ms5837.py /home/pi/Documents/Snocam_scripts')

# Set pi to launch rest of script after reboot
os.system("sudo sed -i '/# Print the IP/isudo python /home/pi/Documents/Snocam_tools/RTC_Finish.py\n\n' /etc/rc.local")

os.system("sudo chmod +x /etc/rc.local")

# Reboot to finish kernel module config
os.system('sudo shutdown now')
