#!/usr/bin/env python3
import os
import string
import secrets
import configparser
import time


def generate_random_string(length):
    # Exclude curly braces '{}' from the pool of characters
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_config_file(config_file_path="config.ini"):
    config = configparser.ConfigParser()

    # Generate random values for password and secret_key with specified lengths
    dj_secret_key = generate_random_string(50)

    # Set the values in the configuration file
    config['internal'] = {
        'secret_key': '{}'.format(dj_secret_key),
        'proj_name': 'labelbase',
        'crypto_salt': 'labelbase_',
        'allowed_host': '*',
        'debug': True,
        'current_timestamp_seconds': int(time.time())
    }

    config['database'] = {
        'name': 'labelbase',
        'user': 'ulabelbase',
        'password': 'vrZvZmX6Kp16B9tTa8JAA4RtAkWEhi',
    #    'host': '127.0.0.1'
    }

    # Create the configuration file and write the values
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    # Check if the config.ini file exists
    if not os.path.isfile(config_file_path):
        generate_config_file()
    else:
        print("{} already exists.".format(config_file_path))
