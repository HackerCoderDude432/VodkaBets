"""
Short Python script to generate the instance folder which stores the config and databases
"""

# Config File skeleton
config = \
"""{
  "SECRET_KEY": <enter_secret_key_here>,
  "SESSION_TOKEN_LENGTH": 35
}"""

import os

# Check if instance folder has already been created
instance_folder = os.path.join(os.getcwd(), "instance")
if os.path.isdir(instance_folder):
    print("Instance folder has already been created!")
    exit()

# make instance folder
os.mkdir(instance_folder)
print("Generated 'instance' directory")

# make skeleton config
with open(os.path.join(instance_folder, "config.json"), "w") as cfg:
    cfg.write(config)
print("Generated config file")

print("NOTE: Databases are generated on first-run of website")
