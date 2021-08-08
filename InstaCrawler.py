import os
import json
import codecs
from time import sleep
from instagram_private_api import Client, ClientCookieExpiredError,      ClientLoginRequiredError, ClientError
from rich.console import Console


class Instagram:


    def __init__(self):

        os.system("clear")
        self.console = Console()
        credentials = self.get_credentials()

        if credentials:
            self.username = credentials['username']
            self.password = credentials['password']

        self.api = self.login()


    def get_credentials(self):

        cred_file = "config/credentials.json"

        if os.path.isfile(cred_file):
            with open(cred_file, "r") as read_file:
                credentials = json.load(read_file)
            self.console.print("Credentials Found...\nAttempting Login...", style="bold red")

            return credentials

        else:
            self.console.print("No Credentials File Found!", style="bold green")
            self.console.print("Create \'config/credentials.json\' file and put your following Credentials", style="bold green")
            self.console.print("{\nusername: {username},\npassword: {password}\n}", style="bold green")


    def login(self):

        try:
            settings = self.get_settings()
            if settings == None:

                try:

                    self.api = Client(
                            auto_patch=True,
                            authenticate=True,
                            username=self.username,
                            password=self.password
                            )

                    self.save_cookies(self.api)

                except:
                    self.console.print("Wrong Credentials...Check Your Username and Password", style="bold green")

            elif settings:

                self.api = Client(
                        auto_patch=True,
                        authenticate=True,
                        username=self.username,
                        password=self.password,
                        settings=settings
                        )

            self.console.print(f"Logged in as {self.username}", style="bold red")

            return self.api

        except Exception as e:
            self.console.print("Login Error...\nDelete the settings file in config directory and re run the script...", style="bold green")


    def get_settings(self):

        if os.path.isfile("config/settings.json"):
            with open("config/settings.json", "r") as read_file:
                cache = json.load(read_file, object_hook=self.from_json)

            return cache

        else:
            self.console.print("No Settings File Found...\nInitiate New Login", style="bold yellow")


    def save_cookies(self, api):

        cache = api.settings
        filename = "config/settings.json"

        with open(filename, "w") as write_file:
            json.dump(cache, write_file, default=self.to_json)


    def to_json(self, python_object):

        if isinstance(python_object, bytes):

            return {
                    "__class__": "bytes",
                    "__value__": codecs.encode(python_object, "base64").decode()
                    }

        raise TypeError(repr(python_object) + ' is not JSON serializable')


    def from_json(self, json_obj):

        if '__class__' in json_obj and json_obj['__class__'] == 'bytes':

            return codecs.decode(json_obj['__value__'].encode(), 'base64')

        return json_obj


    def get_target(self):

        if os.path.isfile("targets.txt"):
            with open("targets.txt", "r") as target_file:
                target_users = target_file.read().splitlines()

            return target_users

        else:
            self.console.print("No Targetd File Found...", style="bold green")
            self.console.print("Create a file 'targets.txt' and put the usernames you want to crawl from Instagram in it", style="bold green")


    def crawl(self):

        target_users = self.get_target()

        if not len(target_users) > 0:

            for user in target_users:
                self.console.print(f"Crawling Details About {user}...", style="bold blue")
                details = self.get_user_details(user)

        else:
            self.console.print("Please Provide Target Usernames in Targets File...", style="bold yellow")


        self.console.print("Finished Crawling...", style="bold red")


    def get_user_details(self, username):

        try:
            endpoint = f"users/{username}/full_detail_info"
            full_data = self.api._call_api(endpoint)

            if full_data:

                content = full_data['user_detail']['user']

            self.save_response(content, username)
            self.console.print(f"Finished...Result Saved Into {username}.json", style="bold blue")

        except ClientError as e:

            self.console.print(f"{username} Not Found", style="bold green")

        except AttributeError as e:

            self.console.print("Please Re Login...", style="bold green")


    def save_response(self, content, username):

        filename = f"output/{username}.json"
        if not os.path.isfile(filename):
            os.mknod(filename)

        with open(filename, "w") as json_file:
            json.dump(content, json_file, indent=True)


instagram = Instagram()
instagram.crawl()
