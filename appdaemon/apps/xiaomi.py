import appdaemon.plugins.hass.hassapi as hass
import time


class Button(hass.Hass):

    def initialize(self):
        for switch in self.args["bedroom_switch"]:
            self.listen_event(self.bedroom_switch, "xiaomi_aqara.click", entity_id = switch)
        
        for switch in self.args["outside_switch"]:
            self.listen_event(self.outside_switch, "xiaomi_aqara.click", entity_id = switch)
        
        for switch in self.args["doorbell"]:
            self.listen_event(self.doorbell, "xiaomi_aqara.click", entity_id = switch)

    def bedroom_switch(self, event_name, data, kwargs):
        click_type = data["click_type"]
        click_dev = data["entity_id"]
        
        if click_type == "single":
            dev = "light.Bedroom"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("light/toggle", entity_id = dev)
          
        elif click_type == "long_click_press":
            dev = "switch.master_switch"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.turn_off(dev)
        
        elif click_type == "double":
            dev = "switch.template_soniq_tv"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)


    def outside_switch(self, event_name, data, kwargs):
        click_type = data["click_type"]
        click_dev = data["entity_id"]

        if click_type == "single":
            dev = "switch.arlec_1b"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)

        elif click_type  == "double":
            dev = "switch.arlec_1c"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)


    def doorbell(self, event_name, data, kwargs):
        
        # if data["click_type"] == "single":
        #     script = "script/doorbell_1" if self.anyone_home() else "script/doorbell_2"
        #     self.log(f"Doorbell pressed...executing {script}")
        #     self.call_service(script)
        
        if self.anyone_home():
            self.call_service("xiaomi_aqara/play_ringtone", gw_mac = self.args["gw_mac"],
                                ringtone_id = "10001", ringtone_vol = "25")

        self.call_service("light/lifx_effect_pulse", entity_id = "group.all_lights", 
                            brightness = "255", color_name = "green", period = "0.4", cycles = "10")

        # if self.anyone_home():
        #     self.call_service("media_player/play_media", entity_id = "media_player.google_home_group", 
        #                         media_content_id = self.args["media_content_id"], media_content_type = "music")

        t = time.strftime("%d-%b-%Y %H:%M:%S")
        message = f"{t}: Doorbell pressed"
        self.log(message)
        self.notify(message, name = "html5")


class Motion(hass.Hass):

    def initialize(self):
        self.handle = None
        self.light = self.args["light"]
        self.sensor = self.args["sensor"]
        self.duration = self.args["duration"]

        self.listen_state(self.motion, self.args["sensor"], new = "on")


    def motion(self, entity, attribute, old, new, kwargs):

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
