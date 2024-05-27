from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import time

import configparser

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration
config.read('config.ini')

class InfluxDBManager:
    def __init__(self):
        self.client = InfluxDBClient(url=config['InfluxDB']['url'], token=config['InfluxDB']['token'], org=config['InfluxDB']['org'])
        self.bucket = config['InfluxDB']['bucket']
        self.org = config['InfluxDB']['org']

    def send_InfluxDB(self, field, value):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point(config['InfluxDB']['measurement'])
            .tag(config['InfluxDB']['nametag1'],config['InfluxDB']['valuetag1'])
            .field(field, value)
        )
        write_api.write(bucket=self.bucket, org=self.org, record=point)
        time.sleep(1)