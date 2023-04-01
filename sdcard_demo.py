import gc
import machine
import sdcard

pdc = machine.Pin(8, machine.Pin.OUT, machine.Pin.PULL_DOWN)
pcs = machine.Pin(9, machine.Pin.OUT,machine.Pin.PULL_UP)
prst = machine.Pin(15, machine.Pin.OUT,machine.Pin.PULL_UP)
pbl = machine.Pin(13, machine.Pin.OUT,machine.Pin.PULL_UP)

gc.collect()  # Precaution before instantiating framebuf
# Max baudrate produced by Pico is 31_250_000. ST7789 datasheet allows <= 62.5MHz.
# Note non-standard MISO pin. This works, verified by SD card.
spi = machine.SPI(1, 60_000_000, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))

# Optional use of SD card. Requires official driver. In my testing the
# 31.25MHz baudrate works. Other SD cards may have different ideas.
from sdcard import SDCard
import os
sd = SDCard(spi, machine.Pin(22, machine.Pin.OUT), 30_000_000)
os.mount(sd, "/sd")

with open("/sd/test.txt", "w") as f:
    f.write("Hello world!\r\n")

def print_directory(path, tabs = 0):
    for file in os.listdir(path):
        stats = os.stat(path+"/"+file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000
    
        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize/1000)
        else:
            sizestr = "%0.1f MB" % (filesize/1000000)
    
        prettyprintname = ""
        for i in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
        
        # recursively print directory contents
        if isdir:
            print_directory(path+"/"+file, tabs+1)


print("Files on filesystem:")
print("====================")
print_directory("/sd")
