
import os
import sys
import socket
from threading import *

import PySimpleGUI as w

from tools.tools import *

# run command if failure: >$: export PYTHONPATH=/path/to/parent:$PYTHONPATH


'''
todo:
- fix multiple enter button bindings
- if
'''

def run_window():
    log("running GUI...")

    window = open_window("host")

    tables_values = []

    while True:
        event, values = window.read()
        if event == w.WIN_CLOSED:
            break
        elif event == CONNECT_BUTTON_LABEL:
            hostname = values["hostname"]
            port     = values["port"]
            username = values["username"]
            speed    = values["speed"]

            new_entry = [values["speed"], values["hostname"], values["port"]]

            log(f'connecting to {hostname}:{port} set to {speed}...')
            # window["output"].print(f'connecting to {hostname}:{port}...')

            # table new connection information
            if new_entry not in tables_values:
                tables_values.append(new_entry)
                table = window.find_element("table")
                table.update(values = tables_values, num_rows = len(tables_values))

        elif event == SEARCH_BUTTON_LABEL:
            keyword  = values["keyword"]

            log(f'searching for keyword \'{keyword}\'...')

        elif event == COMMAND_BUTTON_LABEL:
            command  = values["command"]

            log(f'command entered: {command}')

            # log actions onto GUI
            # window["output"].print(f'>> {command}:')

    window.close()

def run_server():
    log("running server...")

def main():

    launch_window = Thread(target = run_window)
    launch_window.start()

    launch_server = Thread(target = run_server)
    launch_server.start()

    launch_window.join()
    launch_server.join()

if __name__ == '__main__':
    main()