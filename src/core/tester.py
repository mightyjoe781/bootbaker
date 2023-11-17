from src.config import STAND_TEST_ROOT
from src.core.configuration import Config
import os
import subprocess
import time

class ConfigTester:
    SCRIPT_DIR = f"{STAND_TEST_ROOT}/script"
    LOG_DIR = f"{STAND_TEST_ROOT}/logs"

    def __init__(self, config: Config):
        self.script_file = f"{config.identifier}.sh"
        self.script_dir = os.path.join(self.SCRIPT_DIR, config.machine_combo)
        self.machine_combo = config.machine_combo

    def run_script(self):
        script = os.path.join(self.script_dir, self.script_file)

        log_file = os.paht.join(self.LOG_DIR, self.machine_combo, self.script_file.replace('.sh', '.txt'))
        process = subprocess.Popen(['/bin/sh', script], stdout=open(log_file, "w"), stderr=subprocess.STDOUT, shell=False)
        return process, log_file, time.time()

    def __str__(self):
        return f"Config({', '.join(f'{attr}={value}' for attr, value in vars(self).items())})"