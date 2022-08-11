from os.path import exists
from sgp30 import SGP30
import logging
import time
import sys

class AirQuality:
    def __init__(self):
        self.sensor = SGP30()
        self.co2 = -1
        self.voc = -1    
        print("Sensor warming up, please wait...")
        self.sensor.start_measurement(self.crude_progress_bar)
        sys.stdout.write('\n')
        self.load_baseline()
        self.update()
        
    def save_baseline(self):
        eco2, tvoc = self.sensor.command('get_baseline')
        with open("sgp30_baseline", "w") as f:
            f.write(f"{eco2};{tvoc}")
         
    def load_baseline(self):
        if not exists("sgp30_baseline"): return
        with open("sgp30_baseline", "r") as f:
            l = f.readline().strip()
            if len(l) == 0: return
            t = [int(i) for i in l.split(";")]
            self.sensor.set_baseline(int(t[0]), int(t[1]))    

    def update(self):
        result = self.sensor.get_air_quality()
        self.co2 = result.equivalent_co2
        self.voc = result.total_voc
    
    def crude_progress_bar(self):
        sys.stdout.write('.')
        sys.stdout.flush()
if __name__ == '__main__':
    aq = AirQuality()
    aq.update()
    print(aq.co2, aq.voc)
