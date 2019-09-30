#!/usr/bin/python3
# 3/25/2019: Skeetzo
# User Class

import json
import time
import os
from datetime import datetime
from re import sub
from decimal import Decimal

from OnlySnarf import driver as OnlySnarf
from OnlySnarf.settings import SETTINGS as settings

PRICE_MINIMUM = 3

class User:

    def __init__(self, data):
        data = json.loads(json.dumps(data))
        # print(data)
        self.name = data.get('name')
        self.username = data.get('username')
        self.id = data.get('id')
        self.messages_from = data.get('messages_from')
        self.messages_to = data.get('messages_to')
        self.messages = data.get('messages')
        self.preferences = data.get('preferences')
        self.last_messaged_on = data.get('last_messaged_on')
        self.sent_images = data.get('sent_images')
        self.subscribed_on = data.get('subscribed_on')
        self.isFavorite = data.get('isFavorite')
        self.statement_history = data.get('statement_history')
        self.started = data.get('started')
        if data.get('messages_to') is None:
            self.messages_to = []
        if data.get('messages') is None:
            self.messages = []
        if data.get('preferences') is None:
            self.preferences = []
        if data.get('sent_images') is None:
            self.sent_images = []
        if data.get('isFavorite') is None:
            self.isFavorite = False
        if data.get('statement_history') is None:
            self.statement_history = []
        try:
            settings.maybePrint("User: {} - {} - {}".format(self.name, self.username, self.id))
        except Exception as e:
            settings.maybePrint(e)
            settings.maybePrint("User: {}".format(self.id))

    def sendMessage(self, message, image, price):
        try:
            print("Sending Message: {} <- {} - {} - ${}".format(self.id, message, image, price))
            OnlySnarf.goto_user(self)
            success = OnlySnarf.enter_message(message)
            if not success:
                return
            image_name = os.path.basename(image)
            if str(image_name) in self.sent_images:
                print("Error: Image Already Sent: {} -> {}".format(image, self.id))
                return False
            success = OnlySnarf.enter_image(image)
            if not success: return False
            if price != None:
                global PRICE_MINIMUM
                if image != None and Decimal(sub(r'[^\d.]', '', price)) < PRICE_MINIMUM:
                    print("Warning: Price Too Low, Free Image")
                    print("Price Minimum: ${}".format(PRICE_MINIMUM))
                success = OnlySnarf.enter_price(price)
                if not success: return False
            if str(settings.DEBUG) == "True":
                self.sent_images.append("DEBUG")
            else:
                self.sent_images.append(str(image_name))
            if str(settings.DEBUG) == "True" and str(settings.DEBUG_DELAY) == "True":
                time.sleep(int(settings.DEBUG_DELAY_AMOUNT))
            success = OnlySnarf.confirm_message()
            if not success: return False
            if str(settings.DEBUG) == "False":
                self.last_messaged_on = datetime.now()
            return True
        except Exception as e:
            settings.maybePrint(e)
            return False

    def equals(self, user):
        # print(str(user.username)+" == "+str(self.username))
        if user.username == self.username:
            return True
        return False

    def toJSON(self):
        return json.dumps({
            "name":str(self.name),
            "username":str(self.username),
            "id":str(self.id),
            "messages_from":str(self.messages_from),
            "messages_to":str(self.messages_to),
            "messages":str(self.messages),
            "preferences":str(self.preferences),
            "last_messaged_on":str(self.last_messaged_on),
            "sent_images":str(self.sent_images),
            "subscribed_on":str(self.subscribed_on),
            "isFavorite":str(self.isFavorite)
        })

    # greet user if new
    def greet(self):
        if self.last_messaged_on == None:
            return print("Error: User Not New")
        print("Sending User Greeting: {}".format(self.username))
        self.sendMessage(message=settings.DEFAULT_GREETING)

    # send refresher message to user
    def refresh(self):
        if self.last_messaged_on == None:
            print("Warning: Never Greeted, Greeting Instead")
            return self.greet()
        elif (timedelta(self.last_messaged_on)-timedelta(datetime())).days < 30:
            return print("Error: Refresher Date Too Early - {}".format((timedelta(self.last_messaged_on)-timedelta(datetime())).days))
        print("Sending User Refresher: {}".format(self.username))
        self.sendMessage(message=settings.user_DEFAULT_REFRESHER)

    # saves chat log to user
    def readChat(self):
        print("Reading Chat: {} - {}".format(self.username, self.id))
        messages = OnlySnarf.read_chat(self.id)
        self.messages = messages[0]
        # self.messages_and_timestamps = messages[1]
        self.messages_to = messages[2]
        self.messages_from = messages[3]
        settings.maybePrint("Chat Read: {} - {}".format(self.username, self.id))

    # saves statement / payment history
    def statementHistory(self, history):
        print("Reading Statement History: {} - {}".format(self.username, self.id))
        OnlySnarf.read_statements(user=self.id)

    # sets as favorite
    def favor(self):
        print("Favoring: {}".format(self.username))
        self.isFavorite = True

    # unsets as favorite
    def unfavor(self):
        print("Unfavoring: {}".format(self.username))
        self.isFavorite = False


def delayForThirty():
    settings.maybePrint("30...")
    time.sleep(10)
    settings.maybePrint("20...")
    time.sleep(10)
    settings.maybePrint("10...")
    time.sleep(7)
    settings.maybePrint("3...")
    time.sleep(1)
    settings.maybePrint("2...")
    time.sleep(1)
    settings.maybePrint("1...")
    time.sleep(1)