# UPS-Lite

This is the (rewritten) script to check the state of the UPS-Lite. It has been extended to publish the current state via MQTT.

# Systemd service
copy the file into "/lib/systemd/system/" 

and then change the permissions 

sudo chmod 644 /lib/systemd/system/UPL_Lite.service

sudo systemctl daemon-reload
sudo systemctl enable UPS_Lite.service

## Wishlist... 
- Powering mode
- Charge state
- Temperature