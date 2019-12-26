#!/usr/bin/env python3
import struct
import smbus
import sys
import time
import paho.mqtt.client as mqtt
import mqtt_config as config

class UPS():
        
        def __init__(self):
                
                # Set the bus port either 1 or 0
                self.bus = smbus.SMBus(1)
                # set low capacity alert for the battery
                self.low_capacity = 20

        def read_voltage(self):

                # This function returns the voltage as float from the UPS-Lite via SMBus object
                address = 0x36
                read = self.bus.read_word_data(address, 2)
                swapped = struct.unpack("<H", struct.pack(">H", read))[0]
                voltage = swapped * 1.25 /1000/16
                return voltage

        def read_capacity(self):
                
                # This function returns the remaining capacitiy in int as precentage of the battery connect to the UPS-Lite
                address = 0x36
                read = self.bus.read_word_data(address, 4)
                swapped = struct.unpack("<H", struct.pack(">H", read))[0]
                capacity = swapped/256
                return int(capacity)
        
        def is_battery_full(self,capacity):
                
                # This function returns True if the battery is full, else return False
                if(capacity == 100):
                        return True
                return False
        
        def is_battery_low(self,capacity):
                
                # This function returns True if the battery capacity is low, else return False
                if(capacity <= self.low_capacity):
                        return True
                return False
             
class MQTT:

        def __init__(self,client_username,client_passwd,broker_ip,broker_port):
                self.broker_ip = broker_ip
                self.broker_port = broker_port
                self.is_connected = False
                self.client = mqtt.Client()
                self.client.username_pw_set(username=client_username,password=client_passwd)

        def connect2broker(self):
                try:
                        self.client.connect(self.broker_ip,self.broker_port) #connect to broker
                        self.is_connected = True
                except:
                        print("connection failed")
                        self.is_connected = False
                        exit(1) #Should quit or raise flag to quit or retry

        def publishState(self,UPS_class):
                if self.is_connected:
                        voltage = UPS_class.read_voltage()
                        print("[-] Publishing: ups-light/voltage %s" % voltage)
                        self.client.publish("ups-light/voltage",voltage)
                        capacity = UPS_class.read_capacity()
                        print("[-] Publishing: ups-light/capacity %s" % capacity)
                        self.client.publish("ups-light/capacity",capacity)

def main():
            
        ups_lite = UPS()
        voltage = ups_lite.read_voltage()
        capacity = ups_lite.read_capacity()
        is_low = ups_lite.is_battery_low(capacity)
        is_full = ups_lite.is_battery_full(capacity)
        if(is_low):
                print("[-] Warning: Low battery")
        elif(is_full):
                print("[-] Battery is fully charged")
        print("[-] Voltage: %s" % voltage)
        print("[-] Capacitiy: %s" % capacity)

        mqtt = MQTT(config.client_username, config.client_passwd, config.broker_ip, config.broker_port)
        mqtt.connect2broker()
        mqtt.publishState(ups_lite)

main()
