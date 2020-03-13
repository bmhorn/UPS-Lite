#!/usr/bin/env python3
import os
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
                self.full_capacity = 100

        def read_prev_values(self):
                # This function is to read the previous capacity to determing battery state
                try:
                    with open("/tmp/ups_lite_capacity.tmp","r") as tmpfile:
                        all_values = tmpfile.read()

                        prev_capacity,prev_state = all_values.split(':')

                except FileNotFoundError:
                        prev_capacity = "1000"
                        prev_state = "Too_soon_to_tell"
                return int(prev_capacity),prev_state


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
                capacity = int(swapped/256)
        
                # Write capacity to tempfile. Needed to determine state.
                tmpfile= open("/tmp/ups_lite_capacity.tmp","w+")
                tmpfile.write(str(capacity))
                tmpfile.close
                # This function returns True if the battery is full, else return False
                return capacity
        
        def read_state(self,capacity,prev_capacity,prev_state):
	        # Write capacity to tempfile. Needed to determine state.
                if(capacity >= self.full_capacity):
                    state = "CHARGED"
                # low if not charging and below 20 based on voltage, else discharging
                elif(int(prev_capacity) > int(capacity)) and (prev_capacity != int(1000)):
                    if(capacity <= self.low_capacity):
                        state = "LOW"
                    else:
                        state = "DISCHARGING"
                elif(int(prev_capacity) > int(capacity)) and (prev_capacity == int(1000)):
                       state = "Too_soon_to_tell"
                elif(int(prev_capacity) < int(capacity)):
                    state = "CHARGING"
                elif(int(prev_capacity) == int(capacity)):
                    state = prev_state
                else:
                    state = "Too_soon_to_tell"
             	
                # Append state to tmp File
                tmpfile= open("/tmp/ups_lite_capacity.tmp","a+")
                tmpfile.write(":")
                tmpfile.write(str(state))
                tmpfile.close
                return state


        def read_temp(self):
                stream = os.popen('/opt/vc/bin/vcgencmd measure_temp')
                temp = stream.read()
                bla, temp = temp.split("=",2)
                return temp

class MQTT:

        def __init__(self,client_username,client_passwd,broker_ip,broker_port):
                self.broker_ip = broker_ip
                self.broker_port = broker_port
                self.is_connected = False
                self.client = mqtt.Client(client_id="ups-lite_1")
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
                        prev_capacity,prev_dev_state = UPS_class.read_prev_values()
			voltage = UPS_class.read_voltage()
			capacity = UPS_class.read_capacity()
			dev_state = UPS_class.read_state(capacity,prev_capacity,prev_dev_state)
        		temp = UPS_class.read_temp()

			print("[-] Publishing: ups-lite/voltage %s" % voltage)
                        self.client.publish("ups-lite/voltage",voltage)
                        time.sleep(1)
                        print("[-] Publishing: ups-lite/capacity %s" % capacity)
                        self.client.publish("ups-lite/capacity",capacity)
                        time.sleep(1)
			print("[-] Publishing: ups-lite/dev_state %s" % dev_state)
                        self.client.publish("ups-lite/dev_state",dev_state)
                        time.sleep(1)
			print("[-] Publishing: ups-lite/temperature %s" % temp)
                        self.client.publish("ups-lite/temperature",temp)
                        time.sleep(1)
			
			self.client.disconnect()
                        self.is_connected = False

def main():
            
        ups_lite = UPS()
        prev_capacity,prev_state = ups_lite.read_prev_values()
        voltage = ups_lite.read_voltage()
        capacity = ups_lite.read_capacity()
        state = ups_lite.read_state(capacity,prev_capacity,prev_state)
        temp = ups_lite.read_temp()

        mqtt = MQTT(config.client_username, config.client_passwd, config.broker_ip, config.broker_port)
        
        while(True):
                mqtt.connect2broker()
                mqtt.publishState(ups_lite)
                time.sleep(300)

main()
