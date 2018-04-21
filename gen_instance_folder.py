#!/bin/python3
"""
Short Python script to generate the instance folder which stores the config and databases
"""

# Config File skeleton
config = \
"""{{
  "SECRET_KEY": {0},
  "SESSION_TOKEN_LENGTH": 35,
  "SALT_LENGTH": 15,
  "MAX_CHAT_MESSAGE_LENGTH": 255,
  "STARTING_VLADS": 500,
  "CRASH_MIN_BET": 10
}}"""

import os
from secrets import token_urlsafe
from shutil import rmtree

# Check if instance folder has already been created
instance_folder = os.path.join(os.getcwd(), "instance")
if os.path.isdir(instance_folder):
    print("Instance folder has already been created! Do you want do delete and regenerate?")
    if input("type 'yes' to regenerate: ").lower() == "yes":
        rmtree(instance_folder)
        print("Deleted old instance")
    else:
        print("Okay, quitting...")
        exit()

# make instance folder
os.mkdir(instance_folder)
print("Generated 'instance' directory")

# make skeleton config
with open(os.path.join(instance_folder, "config.json"), "w") as cfg:
    key = None

    print("Do you want to autogenerate a secret key?")
    if input("type 'yes' to generate one: ").lower() == "yes":
        key = '"' + token_urlsafe() + '"'
        print("Set secret key as random string")
    else:
        key = "<enter_secret_key_here>"
        print("Set secret key as placeholder")

    cfg.write(config.format(key))

print("Generated config file")

print("Please edit the outputted config.json file before running the web app!")
print("NOTE: Databases are generated on first-run of website")
