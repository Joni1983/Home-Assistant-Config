import appdaemon.plugins.hass.hassapi as hass
import time

class Button(hass.Hass):

    def initialize(self):
        
        for button in self.args["buttons"]:
            self.listen_event(self.cb_button, "xiaomi_aqara.click",
                              entity_id = button)


    def cb_button(self, event_name, data, kwargs):
        click_type = data["click_type"]        
        action = None
        for x in self.args["actions"]:
            if click_type == x["click_type"]:
                action = x
        if not action:
            return
        self.log(action)       
        button_type = action["type"] if "type" in action else "standard"

        if button_type == "standard":
            entity_id = action["entity"]
            device, entity = self.split_entity(entity_id)
            service = action["service"]
            self.call_service(f"{device}/{service}", entity_id = entity_id)
        elif button_type == "doorbell":
            self.doorbell(action)


    def doorbell(self, data):

        if self.sun_down():
            self.turn_on(data["light"])
            self.start_timer()

        if self.anyone_home():
            self.call_service("xiaomi_aqara/play_ringtone", 
                               gw_mac = data["gw_mac"],
                               ringtone_id = data["ringtone_id"], ringtone_vol = data["volume"])

        self.call_service("light/lifx_effect_pulse", 
                           entity_id = "group.all_lights", 
                           brightness = "255", color_name = "green", 
                           period = "0.4", cycles = "10")

        if self.anyone_home():
            devices = ["media_player.google_home_main", 
                       "media_player.google_home_bedroom",
                       "media_player.google_home_office"]
            msg = ("There's someone at the door")
            for gh in devices:
                if self.get_state(gh) == "off": 
                    self.call_service("tts/google_say", entity_id = gh,
                                      message = msg)
                    break

        t = time.strftime("%d-%b-%Y %H:%M:%S")
        message = f"{t}: Doorbell pressed"
        self.log(message)
        self.notify(message, name = "html5")


    def start_timer(self):        
        self.handle = self.run_in(self.end_timer, 180)

    def end_timer(self, kwargs):
        self.turn_off(self.light)