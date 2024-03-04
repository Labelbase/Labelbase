#!/usr/bin/env python3
import os
import string
import secrets
import configparser
import time
import os

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return content.strip()


def generate_random_string(length):
    # Exclude curly braces '{}' from the pool of characters
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_config_file(config_file_path="config.ini"):
    config = configparser.ConfigParser()
    # Generate random values where needed
    dj_secret_key = generate_random_string(50)
    #database_password = read_file_content("/run/secrets/mysql_password")
    database_password = os.getenv("MYSQL_PASSWORD")
    crypto_salt = 'labelbase_{}_'.format(generate_random_string(32))

    # Set the values in the configuration file
    config['internal'] = {
        'secret_key': '{}'.format(dj_secret_key),
        'proj_name': 'labelbase',
        'crypto_salt': crypto_salt,
        'allowed_host': '*',
        'debug': True,
        'current_timestamp_seconds': int(time.time()),
    }

    config['database'] = {
        'name': 'labelbase',
        'user': 'ulabelbase',
        'password': database_password,
    #    'host': '127.0.0.1'
    }

    # Create the configuration file and write the values
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    # Check if the config.ini file exists
    if not os.path.isfile(config_file_path):
        generate_config_file()
        print("Config file {} created.".format(config_file_path))
    else:
        print("{} already exists.".format(config_file_path))
