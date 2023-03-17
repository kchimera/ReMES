import machine
import utime

led = machine.Pin("LED", machine.Pin.OUT)

led.off()

led.on()

while True:
    led.toggle()
    utime.sleep(1)
    
    
    

