from pynicotine.pluginsystem import BasePlugin
from pynicotine.config import config
import os
import time

class Plugin(BasePlugin):
    __name__ = "WarNamer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = {
            "usernames": "",
            "min_seconds_between_changes": 3600
        }
        self.metasettings = {
            "usernames": {
                "description": "List of usernames",
                "type": "textview"
            },
            "min_seconds_between_changes": {
                "description": "Minimum seconds between changes",
                "type": "integer",
                "min": 600
            }
        }
        self.logfile_filename = "username_log.txt"


    def get_last_change(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                if not lines:
                    return None
                last_line = lines[-1].strip()

            if not last_line:
                self.log("Could not read logfile.")
                return None
            last_values = last_line.split(",")
            if len(last_values) == 2:
                last_timestamp, last_username = last_values
                self.log(f"Last username change: {last_line}")
                return last_timestamp, last_username
            else:
                self.log("Invalid last change.")
                return None

        except (FileNotFoundError, PermissionError) as e:
            self.log(f"Error reading logfile: {e}")
            return None


    def loaded_notification(self):

        # import inspect
        # attributes = inspect.getmembers(self.config)#, lambda a: not(inspect.isroutine(a)))
        # for attribute, value in attributes:
        #     self.log(f"{attribute}: {value}")

        self.plugin_dir = f'{self.config.data_folder_path}{os.sep}plugins{os.sep}{__name__}'
        self.logfile = self.plugin_dir + os.sep + self.logfile_filename
        self.change_username()


    def save_last_change(self, timestamp=None, username=None, file_path=None):
        try:
            with open(file_path, "w") as file:
                file.write(f"{timestamp},{username}")
        except PermissionError:
            self.log("Permission error. Check logfile permissions.")
        except IOError as e:
            self.log(f"IOError: {e}")
        except Exception as e:
            self.log(f"An unexpected error occurred: {e}")
        return


    def change_username(self):
        last_change = self.get_last_change(self.logfile)
        if last_change is not None:
            last_timestamp, last_username = last_change
            last_timestamp = float(last_timestamp) if last_timestamp.replace(".", "").replace("-", "").isdigit() and last_timestamp.strip() else 0
        else:
            last_timestamp = 0
            last_username = config.sections["server"]["login"]
        now = time.time()
        min_secs = self.settings["min_seconds_between_changes"]
        if min_secs < 1:
            min_secs = 1
        diff = int(now - last_timestamp)
        if diff < min_secs:
            self.log("Username not changed: too soon ({diff} seconds).")
            return


        # remove duplicates and empty lines from list of usernames in settings
        usernames = list(set(filter(None, self.settings["usernames"].splitlines())))
        if len(usernames) < 2:
            self.log("Please add some usernames in the plugin settings.")
            return

        # everything ok, time to change usernames

        import random
        new_username = random.choice(usernames)
        if new_username != last_username:
            self.save_last_change(timestamp=now, username=new_username, file_path=self.logfile)
            config.sections["server"]["login"] = new_username
            config.write_configuration()
            # config.load_config()
            self.log(f"Username changed from {last_username} to {new_username}")
        else:
            self.log("Username not changed: New and old are the same.")
