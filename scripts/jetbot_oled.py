#!/usr/bin/env python
import time

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

import struct
import smbus
import sys

def readVoltage(bus):

     address = 0x36
     read = bus.read_word_data(address, 2)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     voltage = swapped * 1.25 /1000/16
     return voltage


def readCapacity(bus):

     address = 0x36
     read = bus.read_word_data(address, 4)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     capacity = swapped/256
     return capacity

bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)


def get_ip_address(interface):
    if get_network_interface_state(interface) == 'down':
        return None
    cmd = "ifconfig %s | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'" % interface
    return subprocess.check_output(cmd, shell=True).decode('ascii')[:-1]


def get_network_interface_state(interface):
    return subprocess.check_output('cat /sys/class/net/%s/operstate' % interface, shell=True).decode('ascii')[:-1]

# initialization
if __name__ == '__main__':

	# 128x32 display with hardware I2C:
	disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=1, gpio=1) # setting gpio to 1 is hack to avoid platform detection

	# Initialize library.
	disp.begin()

	# Clear display.
	disp.clear()
	disp.display()

	# Create blank image for drawing.
	# Make sure to create image with mode '1' for 1-bit color.
	width = disp.width
	height = disp.height
	image = Image.new('1', (width, height))

	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)

	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	# Draw some shapes.
	# First define some constants to allow easy resizing of shapes.
	padding = -2
	top = padding
	bottom = height-padding
	# Move left to right keeping track of the current x position for drawing shapes.
	x = 0

	# Load default font.
	font = ImageFont.load_default()

	i = 0

	# start running
	while True:
            
		# Draw a black filled box to clear the image.
		draw.rectangle((0,0,width,height), outline=0, fill=0)

		# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
		#cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
		#CPU = subprocess.check_output(cmd, shell = True )
		cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
		MemUsage = subprocess.check_output(cmd, shell = True )
		cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
		Disk = subprocess.check_output(cmd, shell = True )
		batt = readCapacity(bus)
		if batt > 100 :
			batt = 100
		volt = readVoltage(bus)

		if i == 0 :
			char = '|'
		if i == 1 :
			char = '/'
		if i == 2 :
			char = '-'
		if i == 3 :
			char = '\\'
		i += 1
		if i == 4 :
			i = 0

		draw.text((x, top),  "SOC:" + "%3d" % batt + "%  " + "%1.2f" % volt + "V    " + char, font=font, fill=255)
		draw.text((x, top+8),  "wlan0: " + str(get_ip_address('wlan0')), font=font, fill=255)
		draw.text((x, top+16), str(MemUsage.decode('utf-8')),  font=font, fill=255)
		draw.text((x, top+25), str(Disk.decode('utf-8')),  font=font, fill=255)

		# Display image.
		disp.image(image)
		disp.display()
		time.sleep(1)
