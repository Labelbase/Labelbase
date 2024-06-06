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
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_config_file(config_file_path="config.ini"):
    config = configparser.ConfigParser()
    dj_secret_key = generate_random_string(50)
    database_password = os.getenv("MYSQL_PASSWORD")
    crypto_salt = 'labelbase_{}_'.format(generate_random_string(32))

    config['internal'] = {
        'secret_key': '{}'.format(dj_secret_key),
        'proj_name': 'labelbase',
        'crypto_salt': crypto_salt,
        'allowed_host': '*',
        'debug': False,
        'current_timestamp_seconds': int(time.time()),
        'sentry_dsn': 'https://3b833ae08ccc4ff68793e961fff4921c@o4504646963232768.ingest.sentry.io/4504646967361536',
    }

    config['database'] = {
        'name': 'labelbase',
        'user': 'ulabelbase',
        'password': database_password,
    #    'host': '127.0.0.1'
    }

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    if not os.path.isfile(config_file_path):
        generate_config_file()
        print("Config file {} created.".format(config_file_path))
    else:
        print("{} already exists.".format(config_file_path))
