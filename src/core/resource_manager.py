import sys
import queue
import subprocess
import threading
import time
import psutil
import logging

logger = logging.basicConfig()


class ResourceManager():

    def __init__(self, configs) -> None:
        self.cpu_cores = psutil.cpu_count(logical=True)     # Physical CPU
        self.available_memory = psutil.virtual_memory().available     # available memory in bytes
        logger.info(f"Cores: {self.cpu_cores}\nMemory: {self.available_memory}")
        self.memory = 0.75 * self.available_memory
        self.max_workers = min(self.cpu_cores, int(self.memory / (512 * 1024 * 1024))) # Convert bytes to MB
        self.timeout = 90
        self.task_queue = queue.Queue()
        self.worker_threads = []
        self.counters = {
            'passed':0,
            'failed':0,
            'timeout':0
        }
        self.config = configs

    # recusive kill
    def recursive_kill(process):
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    # producer
    def produce_tasks(self, scripts):
        for script in scripts:
            self.task_queue.put(script)

    # consumer
    def consume_tasks(self):
        while True:
            try:
                script = self.task_queue.get(timeout=2)
                log_file = f"../runs/{script.split('/')[-1].replace('.sh', '.txt')}"
                start = time.time()
                process = subprocess.Popen(['/bin/sh', script], stdout=open(log_file, "w"), stderr=subprocess.STDOUT, shell=False)
                process.communicate(timeout=self.timeout)  # Execute the task
                sys.stdout.write("\r" + " " * 60 + "\r")  # Clear the line
                els_time = time.time() - start
                # check if process was success or not
                if process.returncode == 0:
                    print(f"{script.split('/')[-1]} success in {els_time:.2f}s")
                    self.counters['passed'] += 1
                else:
                    print(f"{script.split('/')[-1]} failed in {els_time:.2f}s")
                    self.counters['failed'] += 1
                self.task_queue.task_done()  # Signaling task completion
            except subprocess.TimeoutExpired:
                self.recursive_kill(process)
                els_time = time.time() - start
                sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
                print(f"{script.split('/')[-1]} timed out in {els_time:.2f}s")
                self.counters['timeout'] += 1
                with open(log_file, 'w') as log:
                    log.write("\n---Script execution timed out---\n")
            except queue.Empty:
                # print(f"Worker {threading.current_thread().name} has no task to execute")
                break  # No tasks left, exit loop        

    def work(self):
        scripts = [ config['script'] for config in self.configs ]
        # producer keeps putting tasks in the queue
        self.producer_thread = threading.Thread(target=self.produce_task, args=(scripts))
        self.producer_thread.start()

        start_time = time.time()
        # list of worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self.consume_tasks, args=(), name=f"Worker-{i+1}")
            worker.start()
            self.worker_threads.append(worker)

        # wait for producer to finish processing jobs
        self.producer_thread.join()

        # Interactive Wait :)
        symbols = [".  ", ".. ", "...", " ..", "  ."]  # Rotating dot symbols
        current_symbol = 0
        while any(worker.is_alive() for worker in self.worker_threads):
            # print(f" [{sum(worker.is_alive() for worker in worker_threads)} / {len(worker_threads)}] Workers Active | [{sum(c for c in counters.values())} / {len(scripts)}] Tasks Completed {symbols[current_symbol % len(symbols)]}", end='\r', flush=True) 
            fill = sum(c for c in self.counters.values())
            # percent = int(fill/(len(script_dir)*10))
            print(f" [{'='*fill*2}>{' '*(20-fill)}]({fill} / {len(scripts)}) Tasks Completed {symbols[current_symbol % len(symbols)]}", end='\r', flush=True) 
            current_symbol = (current_symbol + 1) % len(symbols)
            time.sleep(0.5)

        elapsed_time = time.time() - start_time
        sys.stdout.write("\r" + " " * 60 + "\r")  # Clear the line
        print(f"Total Time Elapsed: {elapsed_time:.2f}s")
        print("\nSummary : \n{} Passed\n{} Failed".format(self.counters['passed'], self.counters['failed'] + self.counters['timeout']))






