import Adafruit_DHT
import config as cfg
import logging 

class DHT11:
    def __init__(self):
        self.temperature = -1
        self.humidity = -1
        
    def update(self):
        h, t = Adafruit_DHT.read_retry(11, cfg.DHT11)
        if h != None:
            self.humidity = h
        if t != None:
            self.temperature = t
