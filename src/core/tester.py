from src.config import STAND_TEST_ROOT
from src.core.configuration import Config
import os
import subprocess
import time

class ConfigTester:
    SCRIPT_DIR = f"{STAND_TEST_ROOT}/script"
    LOG_DIR = f"{STAND_TEST_ROOT}/logs"
    target_string = "RC COMMAND RUNNING -- SUCCESS!!!"
    timeout = 60

    def __init__(self, config: Config):
        self.config = config
        self.script_file = f"{config.identifier}.sh"
        self.script_dir = os.path.join(self.SCRIPT_DIR, config.machine_combo)
        self.machine_combo = config.machine_combo
        self.log_path = os.path.join(self.LOG_DIR, self.machine_combo)
        self.log_file = os.path.join(self.log_path, self.script_file.replace('.sh', '.log'))
        os.makedirs(self.LOG_DIR,exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)
    
    def run_qemu_script(self):
        script = os.path.join(self.script_dir, self.script_file)
        start = time.time()
        process = subprocess.Popen(['/bin/sh', script], stdout=open(self.log_file, "w"), stderr=subprocess.STDOUT, shell=False)
        process.communicate(timeout=self.timeout)  # Execute the task
        return process, time.time() - start


    def run_test(self):
        try:
            process, els_time = self.run_qemu_script()
            if process.returncode == 0:
                # validate log file contains validation string
                with open(self.log_file, 'r', errors='replace') as f:
                    contents = f.read()
                    if self.target_string in contents:
                        print(f"{self.script_file.split('/')[-1]} success in {els_time:.2f}s")
                    else:
                        print("RC COMMAND String not found!")
                        return False
            else:
                print(f"{self.script_file.split('/')[-1]} failed in {els_time:.2f}s")
                return False
            # test passed
            return True
        except UnicodeDecodeError as e:
            # this should not occur if errors='replace' selected while opening
            print(f"Error decoding file: {e}")
        except FileNotFoundError:
            print(f"Error: Log file '{self.log_file}' not found.")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def __str__(self):
        return f"Config({', '.join(f'{attr}={value}' for attr, value in vars(self).items())})"