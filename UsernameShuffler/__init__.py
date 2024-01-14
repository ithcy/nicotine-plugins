from pynicotine.pluginsystem import BasePlugin
from pynicotine.config import config

class Plugin(BasePlugin):
    __name__ = "UsernameShuffler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = {
            "usernames": ""
        }
        self.metasettings = {
            "usernames": {
                "description": "List of usernames",
                "type": "textview"
            }
        }

    def loaded_notification(self):
        self.change_username()

    def change_username(self):
        old_username = config.sections["server"]["login"]
        usernames = self.settings["usernames"].splitlines()
        if len(usernames) < 1:
            self.log("Please add some usernames in the plugin settings")
            return
        import random
        new_username = random.choice(usernames)
        if new_username != old_username:
            config.sections["server"]["login"] = new_username
            config.write_configuration()
            config.load_config()
            self.log(f"Username changed from {old_username} to {new_username}")
        else:
            self.log("Username not changed")
