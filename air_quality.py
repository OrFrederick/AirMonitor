from os.path import exists
from sgp30 import SGP30
import logging
import time
import sys
import config as cfg

class AirQuality:
    def __init__(self):
        self.sensor = SGP30()
        self.co2 = -1
        self.voc = -1    
        self.co2_baseline = 0
        self.voc_baseline = 0

        print("Sensor warming up, please wait...")
        self.sensor.start_measurement()
        self.found_baseline = self.load_baseline()
        self.update()
        
    def save_baseline(self):
        eco2, tvoc = self.sensor.command('get_baseline')
        with open(cfg.BASELINE, "w") as f:
            f.write(f"{eco2};{tvoc}")
            self.co2_baseline = eco2
            self.voc_baseline = tvo
            print("Saved baseline")

    def set_humidity(self, humidity):
        self.sensor.command("set_humidity", [round(humidity)])
        print("Set new humidity", humidity, round(humidity))

    def load_baseline(self):
        print(cfg.BASELINE)
        if not exists(cfg.BASELINE): return False
        with open(cfg.BASELINE, "r") as f:
            l = f.readline().strip()
            if len(l) == 0: return
            t = [int(i) for i in l.split(";")]
            self.sensor.set_baseline(int(t[0]), int(t[1]))
            self.co2_baseline = int(t[0])
            self.voc_baseline = int(t[1])
            print("Loaded baseline")
        return True
    
    def update(self):
        result = self.sensor.get_air_quality()
        self.co2 = result.equivalent_co2
        self.voc = result.total_voc
    
