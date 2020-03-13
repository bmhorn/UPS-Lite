# UPS-Lite
This is a (rewritten) script to check the state of the UPS-Lite. It has been extended to publish the current state via MQTT. The topics are hardcoded
- ups-lite/voltage
- ups-lite/capacity
- ups-lite/temperature
- ups-lite/dev_state

It is still a work in progress.

# MQTT
All relevant date to connect to the broker are stored in the file mqtt_config.py. There exists an example file named mqtt_config_default.py. Before you can start, you need of course an MQTT-Broker and you need to install paho-mqtt via `sudo pip3 install paho-mqtt`

# Systemd service
copy the file "UPS_Lite.service" into "/lib/systemd/system/"
`sudo cp UPS_Lite.service /lib/systemd/system/UPS_Lite.service`

and then change the permissions with
`sudo chmod 644 /lib/systemd/system/UPS_Lite.service`

afterwards reload systemd-daemon
`sudo systemctl daemon-reload`

and enable service
`sudo systemctl enable UPS_Lite.service`

## Wishlist... 
- Powering mode
- Charge state
