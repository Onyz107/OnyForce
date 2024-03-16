import logging
import os
import signal
import threading
import subprocess

RUNNING = True


def get_tor_process_ids():
    try:
        output = subprocess.check_output(["pgrep", "tor"])
        return [int(pid) for pid in output.split()]
    except subprocess.CalledProcessError:
        return []


def refresh_tor_ips():
    tor_pids = get_tor_process_ids()
    if tor_pids:
        for pid in tor_pids:
            try:
                os.kill(pid, signal.SIGHUP)
                logging.debug("SIGHUP signal sent to TOR process (PID: {})".format(pid))
            except OSError as e:
                logging.error("Failed to send SIGHUP signal to PID {}: {}".format(pid, e))
    else:
        logging.debug("TOR processes not found.")

    if RUNNING:
        threading.Timer(10, refresh_tor_ips).start()


if __name__ == "__main__":
    refresh_tor_ips()





