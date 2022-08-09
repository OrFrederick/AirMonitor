from RPi import GPIO
import logging

class RotaryEncoder:
    def __init__(self, sw, clk, dt):  
        # GPIOs zum Rotary Encoder
        self.sw = sw
        self.clk = clk
        self.dt = dt
        self.value = 0
        self.btnToggled = False
 
        #tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
        GPIO.setmode(GPIO.BCM) 
         
        #set up the GPIO events on those pins
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        #set up the interrupts
        GPIO.add_event_detect(self.clk, GPIO.FALLING, callback=self.clkClicked, bouncetime=300)
        GPIO.add_event_detect(self.dt, GPIO.FALLING, callback=self.dtClicked, bouncetime=300)
        GPIO.add_event_detect(self.sw, GPIO.FALLING, callback=self.swClicked, bouncetime=300)
        
    #define functions which will be triggered on pin state changes
    def clkClicked(self, channel):
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)
 
        if clkState == 0 and dtState == 1:
            self.value += 1
 
    def dtClicked(self, channel): 
        clkState = GPIO.input(self.clk)
        dtState = GPIO.input(self.dt)
         
        if clkState == 1 and dtState == 0:
            self.value -= 1
 
    def swClicked(self, channel):
        self.btnToggled = not self.btnToggled

    def __del__(self):
        GPIO.cleanup()

if __name__ == '__main__':
    import config as cfg
    renc = RotaryEncoder(*cfg.ROTARY_ENCODER)
    while True:
        print(renc.value)
