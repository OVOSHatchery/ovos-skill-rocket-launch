from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
import requests
from datetime import datetime, timedelta
from lingua_franca.format import nice_date, nice_duration


class SpaceLaunchSkill(OVOSSkill):
    # https://www.rocketlaunch.live/api
    # https://launchlibrary.net/
    @intent_handler(
        IntentBuilder("SpaceLaunchIntent").require("SpaceLaunchKeyword").
        optionally('ExactLaunchKeyword').optionally("next"))
    def handle_space_launch_intent(self, message):
        try:
            r = requests.get("https://launchlibrary.net/1.2/launch/next/1"
                             "").json()
            dt = datetime.strptime(r['launches'][0]["windowstart"],
                                   "%B %d, %Y %H:%M:%S UTC")
            image = r['launches'][0]["rocket"]["imageURL"]
            description = str(r['launches'][0]["missions"][0]["description"])
            rocket = str(r['launches'][0]['rocket']['name'])
            location = str(r['launches'][0]['location']['pads'][0]['name'])
            now = datetime.now()
            delta = dt - now
            if delta <= timedelta(days=2):
                date_time = nice_duration(delta, lang=self.lang, speech=True)
                self.speak_dialog("space.launch.delta",
                                  data={
                                      'rocket': rocket,
                                      'delta': date_time,
                                      'location': location
                                  })
            else:
                date_time = nice_date(dt, lang=self.lang, now=now)
                self.speak_dialog("space.launch",
                                  data={
                                      'rocket': rocket,
                                      'time': date_time,
                                      'location': location
                                  })

            self.gui.show_image(
                image,
                caption=location,
                title=rocket,
                override_idle=True,
                fill='PreserveAspectFit',
            )

            self.set_context("launch_description", description)
            self.set_context("rocketPic", image)
            self.set_context("rocket", rocket)

        except Exception as e:
            self.log.error(e)
            self.speak_dialog("not.found")

    @intent_handler(
        IntentBuilder("SpaceLaunchMoreIntent").require("launch_description").
        require("rocket").require("rocketPic").require('MoreKeyword'))
    def handle_space_launch_desc_intent(self, message):
        description = message.data["launch_description"]
        rocket = message.data["rocket"]
        image = message.data["rocketPic"]
        self.speak(description)
        self.gui.show_image(
            image,
            caption=description,
            title=rocket,
            override_idle=True,
            fill='PreserveAspectFit',
        )
