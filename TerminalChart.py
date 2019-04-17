import getpass
from termcolor import colored
from pusher import Pusher
import pysher
from dotenv import load_dotenv
import os
import json

load_dotenv(dotenv_path='.env')


class TerminalChart:
    pusher = None
    channel = None
    chatroom = None
    clientPusher = None
    user = None
    users = {
        "samuel": "samuel'spassword",
        "daniel": "daniel'spassword",
        "tobi": "tobi'spassword",
        "sarah": "sarah'spassword"
    }
    chatrooms = ["sports", "general", "education", "health", "technology"]

    ''' The entry point of the application'''

    def main(self):
        self.login()
        self.select_chatroom()
        while True:
            self.get_input()

    ''' This function handles logon to the system. In a real world app, 
    you might need to connect to API's or a database to verify users '''

    def login(self):
        username = input("Please enter your username: ")
        password = getpass.getpass("Please enter %s's Password:" % username)
        if username in self.users:
            if self.users[username] == password:
                self.user = username
            else:
                print(colored("Your password is incorrect", "red"))
                self.login()
        else:
            print(colored("Your username is incorrect", "red"))
            self.login()

    ''' This function is used to select which chatroom you would like to connect to '''

    def select_chatroom(self):
        print(colored("Info! Available chatrooms are %s" % str(self.chatrooms), "blue"))
        chatroom = input(colored("Please select a chatroom: ", "green"))
        if chatroom in self.chatrooms:
            self.chatroom = chatroom
            self.init_pusher()
        else:
            print(colored("No such chatroom in our list", "red"))
            self.select_chatroom()

    ''' This function initializes both the Http server Pusher as well as the clientPusher'''

    def init_pusher(self):
        self.pusher = Pusher(app_id=os.getenv('PUSHER_APP_ID', None), key=os.getenv('PUSHER_APP_KEY', None),
                             secret=os.getenv('PUSHER_APP_SECRET', None), cluster=os.getenv('PUSHER_APP_CLUSTER', None))
        self.clientPusher = pysher.Pusher(os.getenv('PUSHER_APP_KEY', None), os.getenv('PUSHER_APP_CLUSTER', None))
        self.clientPusher.connection.bind('pusher:connection_established', self.connect_handler)
        self.clientPusher.connect()

    ''' This function is called once pusher has successfully established a connection'''

    def connect_handler(self, data):
        self.channel = self.clientPusher.subscribe(self.chatroom)
        self.channel.bind('newmessage', self.pusher_callback)

    ''' This function is called once pusher receives a new event '''

    def pusher_callback(self, message):
        message = json.loads(message)
        if message['user'] != self.user:
            print(colored("{}: {}".format(message['user'], message['message']), "blue"))
            print(colored("{}: ".format(self.user), "green"))

    ''' This function is used to get the user's current message '''

    def get_input(self):
        message = input(colored("{}: ".format(self.user), "green"))
        self.pusher.trigger(self.chatroom, u'newmessage', {"user": self.user, "message": message})


if __name__ == "__main__":
    TerminalChart().main()
