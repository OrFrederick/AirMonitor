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

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import config as cfg

class Main:
    def __init__(self):
        self.renc = RotaryEncoder(*cfg.ROTARY_ENCODER)
        self.temperature_sensor = DHT11()
        self.screen = Screen()
        self.air_quality = AirQuality()
        self.cur_page = 0
        t = threading.Thread(target=self.update_measurings, args=(), daemon = True)
        t.start()
 
        # InfluxDB
        token = cfg.INFLUX_DB_TOKEN  #  "c9Z6r5hiJ9HyKTTQViYVu0G6DQP2OgUsC6KBMxDfswCr-RJgEQNOqDFgo-EY3k5AgTMeHQvu198Bhn13UWauSQ=="
        org = cfg.INFLUX_DB_ORG #  "frederick.ortmanns@gmail.com"
        url = cfg.INFLUX_DB_URL # "https://europe-west1-1.gcp.cloud2.influxdata.com"

        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        
        t2 = threading.Thread(target=self.send_to_influxdb, args=(), daemon = True)
        t2.deamon = True
        t2.start()

    # Logs the data to your InfluxDB
    def send_to_influxdb(self):
        bucket="PiZimmer"
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
            
        while True:
            dtime = datetime.utcnow()
            disk = psutil.disk_usage('/')
            mem = psutil.virtual_memory()
            load = psutil.getloadavg()
            
            body = [
                    {
                        "measurement": "system",
                        "time": dtime,
                        
                        "fields": {
                            "load_1": load[0],
                            "load_5": load[1],
                            "load_15": load[2],
                            "disk_percent": disk.percent,
                            "disk_free": disk.free,
                            "disk_used": disk.used,
                            "mem_percent": mem.percent,
                            "mem_free": mem.free,
                            "mem_used": mem.used
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
        last_change = 0
        last_value = -1
        while True:
            time.sleep(0.5)
            passed_secs += 0.5
            if passed_secs >= 3600:
                print("SAVED NEW BASELINE")
                self.air_quality.save_baseline()
                passed_secs = 0

            if self.renc.btnToggled:
                time.sleep(2)
                passed_secs += 2
                if self.screen.on:
                    self.screen.disp.command(0xAE)
                    self.screen.on = False
                continue
            elif not self.screen.on:
                self.screen.disp.command(0xAF)
                self.screen.on = True

            (sw, sh) = (128, 64)

            dtime = datetime.now().strftime("%H:%M:%S")
            date = datetime.now().strftime("%d.%m.%Y")
            pages = [
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "Temperature", 2], [(sw-25, sh-18), "1/4", 2], [(5, 3), dtime, 0], [(sw-75, 3), date,0], [self.screen.get_center_coords(f"{self.temperature_sensor.temperature}°C", 1), f"{self.temperature_sensor.temperature}°C", 1]]),
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "Humidity", 2], [(sw-25, sh-18), "2/4", 2], [(5, 3), dtime, 0], [(sw-75, 3), date, 0], [self.screen.get_center_coords(f"{self.temperature_sensor.humidity}%", 1), f"{self.temperature_sensor.humidity}%", 1]]),           
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "CO2", 2], [(sw-25, sh-18), "3/4", 2], [(5, 3), dtime, 0], [(sw-75, 3), date, 0], [self.screen.get_center_coords(f"{self.air_quality.co2}ppm", 1), f"{self.air_quality.co2}ppm", 1]]),
                Page([[(0,0),(sw-1,0)], [(0,0),(0,sh-1)], [(0,sh-1),(sw-1,sh-1)], [(sw-1,0),(sw-1, sh-1)]], [[(5, sh-18), "VOC", 2], [(sw-25, sh-18), "4/4", 2], [(5, 3), dtime, 0], [(sw-75, 3), date, 0], [self.screen.get_center_coords(f"{self.air_quality.voc}ppb", 1), f"{self.air_quality.voc}ppb", 1]]),
            ]          
            
            
            self.cur_page = abs(self.renc.value) % len(pages)
            
            # Every 10 Seconds: Go to next page
            if self.renc.value != last_value:
                last_change = 0
                last_value = self.renc.value
            else:
                last_change += 0.5
            
                if last_change % 10 == 0:
                    self.renc.value += 1                 
                    self.renc.value %= len(pages)
            self.screen.draw_page(pages[self.cur_page])
if __name__ == '__main__':
    m = Main()
    m.main()
