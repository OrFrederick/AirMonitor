import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
FONTS = os.path.dirname(os.path.abspath(__file__)) + '/fonts'
# sw clk dt
ROTARY_ENCODER = (17, 23, 22)
SHUTDOWN_BTN = 24
DHT11 = 4
INFLUX_DB_TOKEN  = os.environ.get("INFLUX_DB_TOKEN")
INFLUX_DB_ORG = os.environ.get("INFLUX_DB_ORG")
INFLUX_DB_URL = os.environ.get("INFLUX_DB_URL") 
