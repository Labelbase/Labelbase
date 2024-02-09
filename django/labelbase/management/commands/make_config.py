from django.core.management.base import BaseCommand
import subprocess
import os


class Command(BaseCommand):
    help = 'Make inital Labelbase config'

    def handle(self, *args, **options):
        from labellabor.make_config import generate_config_file
        config_file_path = "config.ini"
        try:
            if not os.path.isfile(config_file_path):
                generate_config_file()
            else:
                print("{} already exists.".format(config_file_path))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Error creating Labelbase config. {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Labelbase config created successfully."))
