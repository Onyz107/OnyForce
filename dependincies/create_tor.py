import os
import subprocess
import colorama
import threading
import time
import psutil
import logging
import concurrent.futures

data_directories = []


def kill_tor_instances():
    tor_processes = []

    # Iterate through all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if the process name contains 'tor'
            if 'tor' in proc.info['name'].lower():
                tor_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if tor_processes:
        print(f"\n{colorama.Fore.YELLOW}{colorama.Style.BRIGHT}Found TOR instances. Killing...{colorama.Fore.RESET}{colorama.Style.RESET_ALL}")
        for proc in tor_processes:
            proc.kill()
        print(f"\n{colorama.Fore.GREEN}{colorama.Style.BRIGHT}TOR instances killed successfully.{colorama.Fore.RESET}{colorama.Style.RESET_ALL}")


def animation(text: str, lock: threading.Event):
    while not lock.is_set():
        print(f'\033[K{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}[!] {text}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}\033[G', end='', flush=True)
        time.sleep(0.4)
        print(f'\033[K{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}[!] {text}.{colorama.Fore.RESET}{colorama.Style.RESET_ALL}\033[G', end='', flush=True)
        time.sleep(0.4)
        print(f'\033[K{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}[!] {text}..{colorama.Fore.RESET}{colorama.Style.RESET_ALL}\033[G', end='', flush=True)
        time.sleep(0.4)
        print(f'\033[K{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}[!] {text}...{colorama.Fore.RESET}{colorama.Style.RESET_ALL}\033[G', end='', flush=True)
        time.sleep(0.4)




class Make_tor_processes:
    def __init__(self, number_of_processes: int):
        kill_tor_instances()
        for number in range(number_of_processes):
            os.makedirs(f'/tmp/tor_data_directory_{number}', exist_ok=True)
            data_directories.append(f'/tmp/tor_data_directory_{number}')


        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_processes) as executor:
            _ = executor.map(self.make_tor_instance, [directory for directory in data_directories])


    @staticmethod
    def make_tor_instance(directory):
        tor_process = subprocess.Popen(
            f'tor -SocksPort {10000 + data_directories.index(directory)} --DataDirectory {directory}',
            stdout=subprocess.PIPE, shell=True)

        lock = threading.Event()

        threading.Thread(target=animation,
                         args=(f'Starting TOR process on port {10000 + data_directories.index(directory)}', lock),
                         daemon=True).start()

        while 1:
            stdout = tor_process.stdout.readline()

            if stdout and b'Bootstrapped' in stdout:
                logging.debug(stdout.decode())
                if b'100%' in stdout:
                    lock.set()
                    print(
                        f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}[+] Started TOR process on port {10000 + data_directories.index(directory)} successfully{colorama.Style.RESET_ALL}{colorama.Fore.RESET}')
                    break


