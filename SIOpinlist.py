# this file contains a list of RPi GPIO pins used by SIO
O_spray_solenoid         = 19 #pi35
O_plunger_solenoid       = 13 #pi33
I_cryostat_sensor_sig    = 21 #pi40
I_plunger_irsensor_sig   = 20 #pi38
O_spray_pwr              = 26 #pi37
O_cryostat_sensor_pwr    = 6 #pi31

# new additions
O_plunger_irsensor_enable = 12 #pi32
O_spray_ctrl              = 16 #pi36

# HW changes to original SIO design: 
# 1) Plunger IR sensor enable pin added 
# 2) Spray control pin added (MOSFET controls power to piezo spray))
# 3) Cryostat sensor (interlock) changed to simple reed switch and pin to pullup. (switch normally open, when closed it pulls down pin to gnd)


