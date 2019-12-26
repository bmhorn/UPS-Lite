# UPS-Lite

This is the (rewritten) script to check the state of the UPS-Lite. It has been extended to publish the current state via MQTT.

# MQTT
All relevant date to connect to the broker are stored in the file mqtt_config.py. There exists an example file named mqtt_config_default.py

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
- Temperature