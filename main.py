import RPi.GPIO as GPIO 
from rotary_encoder import RotaryEncoder
from dht11 import DHT11
from screen import Screen
from page import Page
import shutdown_btn
from air_quality import AirQuality

from datetime import datetime
from PIL import ImageFont
import threading
import psutil
from atmos import calculate

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import config as cfg

class Main:
    def __init__(self):
        print(datetime.utcnow())
        self.renc = RotaryEncoder(*cfg.ROTARY_ENCODER)
        self.temperature_sensor = DHT11()
        self.screen = Screen()
        self.air_quality = AirQuality()
        
        self.cur_page = 0
        self.finished_calibration = self.air_quality.found_baseline

        t = threading.Thread(target=self.update_measurings, args=(), daemon = True)
        t.start()
 
        # InfluxDB
        token = cfg.INFLUX_DB_TOKEN
        org = cfg.INFLUX_DB_ORG
        url = cfg.INFLUX_DB_URL

        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        if cfg.USE_INFLUX_DB:
            t2 = threading.Thread(target=self.send_to_influxdb, args=(), daemon = True)
            t2.deamon = True
            t2.start()

    # Logs the data to your InfluxDB
    def send_to_influxdb(self):
        bucket="PiZimmer"
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
            
        while True:
            dtime = datetime.utcnow()
            load = psutil.getloadavg()
            
            body = [
                    {
                        "measurement": "system",
                        "time": dtime,
                        
                        "fields": {
                            "load_1": load[0],                         
                            "cpu_temp": psutil.sensors_temperatures()['cpu_thermal'][0].current,
                        }
                    }
                ]
            
            if self.temperature_sensor.temperature != -1 and self.temperature_sensor.temperature != None:
                body.append({
                    "measurement" : "Zimmer",
                    "time": dtime,
                    "fields" : {
                        "temperature": self.temperature_sensor.temperature,
                        "humidity": self.temperature_sensor.humidity,
                        "CO2": self.air_quality.co2,
                        "VOC": self.air_quality.voc,
                        "co2_baseline": self.air_quality.co2_baseline,
                        "voc_baseline": self.air_quality.voc_baseline
                        }
                    })
                try:
                    write_api.write(bucket=bucket, org="frederick.ortmanns@gmail.com", record=body)
                except:
                    print("Failed, sending data to API")
            time.sleep(30)
            
    def update_measurings(self):
        while True:
            self.temperature_sensor.update()
            self.air_quality.update()
    
    def main(self):
        passed_secs = 0

        while True:
            time.sleep(0.5)
            passed_secs += 0.5

            if passed_secs%120 == 0:
                ah = calculate('AH', RH=self.temperature_sensor.humidity, p=1e5, T=round(273.15 + self.temperature_sensor.temperature), debug=True)[0]
                self.air_quality.set_humidity(ah*1000) 

            # Every hour save and reload baseline
            if self.finished_calibration and passed_secs >= 60*60:
                self.air_quality.save_baseline()
                self.air_quality.load_baseline()
                passed_secs = 0

            # Finish calibration after 12 hours
            if not self.finished_calibration and  passed_secs >= 60*60*12:
                self.air_quality.save_baseline()
                self.air_quality.load_baseline()
                passed_secs = 0
                self.finished_calibration = True

            if self.renc.btnToggled:
                time.sleep(2)
                passed_secs += 2
                if self.screen.on:
                    self.screen.disp.command(0xAE)
                    self.screen.on = False
                # Skip drawing the screen
                continue
            elif not self.screen.on:
                self.screen.disp.command(0xAF)
                self.screen.on = True

            (sw, sh) = (128, 64)

            dtime = datetime.now().strftime("%H:%M:%S")
            date = datetime.now().strftime("%d.%m.%Y")
            pages = [
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "Temperature", 2], [(sw-25, sh-18), "1/4", 2], [(5, 3), dtime, 0], [(sw-65, 3), date,0], [self.screen.get_center_coords(f"{self.temperature_sensor.temperature}°C", 1), f"{self.temperature_sensor.temperature}°C", 1]]),
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "Humidity", 2], [(sw-25, sh-18), "2/4", 2], [(5, 3), dtime, 0], [(sw-65, 3), date, 0], [self.screen.get_center_coords(f"{self.temperature_sensor.humidity}%", 1), f"{self.temperature_sensor.humidity}%", 1]]),           
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "CO2", 2], [(sw-25, sh-18), "3/4", 2], [(5, 3), dtime, 0], [(sw-65, 3), date, 0], [self.screen.get_center_coords(f"{self.air_quality.co2}ppm", 1), f"{self.air_quality.co2}ppm", 1]]),
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "VOC", 2], [(sw-25, sh-18), "4/4", 2], [(5, 3), dtime, 0], [(sw-65, 3), date, 0], [self.screen.get_center_coords(f"{self.air_quality.voc}ppb", 1), f"{self.air_quality.voc}ppb", 1]]),
            ]          
            
            self.cur_page = abs(self.renc.value) % len(pages)
            self.screen.draw_page(pages[self.cur_page])
if __name__ == '__main__':
    m = Main()
    m.main()
