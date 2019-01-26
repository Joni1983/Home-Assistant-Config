import appdaemon.plugins.hass.hassapi as hass
import time

class sensor_light(hass.Hass):

    def initialize(self):
        self.handle = None
        self.light = self.args["light"]
        self.sensor = self.args["sensor"]
        self.duration = self.args["duration"]
        self.night_mode = False

        if "night_mode" in self.args:
            self.night_mode = self.args["night_mode"]

        self.listen_state(self.motion, self.args["sensor"], new = "on")


    def motion(self, entity, attribute, old, new, kwargs):
        
        if self.night_mode and self.sun_up():
            return
            
        self.log(f"Motion detected...Turning on {self.light}")
        self.turn_on(self.light)
        self.start_timer()


    def start_timer(self):
        if self.handle != None:
            self.cancel_timer(self.handle)
        
        self.log(f"{self.light} set to turn off in {self.duration} seconds")
        self.handle = self.run_in(self.end_timer, self.duration)


    def end_timer(self, kwargs):
        
        if self.get_state(self.args["sensor"]) == "on":
            self.log("Motion sensor still active...starting new delay")
            self.start_timer()
        else:
            self.log(f"Turning off {self.light}")
            self.turn_off(self.light)


class Alarm(hass.Hass):

    def initialize(self):
        for sensor in self.args["motion_sensors"]:
            self.listen_state(self.cb_alarm_trigger, sensor, new = "on")
    
    
    def cb_alarm_trigger(self, entity, attribute, old, new, kwargs):
        if self.noone_home():
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            msg = f"{t}: Motion detected {entity}"
            self.log(msg)
            self.notify(msg, name = "html5")
