
from PySimpleGUI import Window
import PySimpleGUI as w

CONNECT_BUTTON_LABEL = "Connect"
SEARCH_BUTTON_LABEL  = "Search"
COMMAND_BUTTON_LABEL = "Go"

WINDOW_SIZE = (600, 800)

def log(message : str):
    print(f'[+] - {message}')

def text(label,  size = None, font = None, text_color = None):
    return [w.Text(label, text_color = text_color)]

def user_input(label, key, push = True, default_text = '', size = (40, 1)):
    return  [w.Text(label), w.Push(), w.InputText(key = key, size = size)] if push == True else [w.Text(label), w.InputText(key = key, size = size)]

def drop_down(options, key, enable_events = True):
    return [w.Combo(options, key = key, enable_events = enable_events)]

def button(label, bind = False, size = None, font = None):
    return [w.Button(label, bind_return_key = bind)]

def vertical_line():
    return [w.VerticalSeparator()]

def horizontal_line():
    return [w.HorizontalSeparator()]

def blank_frame():
    return w.Frame("", [[]], pad=(5, 3), expand_x=True, expand_y=True, background_color='#404040', border_width = 0)


def open_window(title : str) -> Window:

    left_column = w.Column(
        [
            user_input("hostname", key = "hostname"),
            user_input("port", key = "port"),
            button(CONNECT_BUTTON_LABEL)
        ]
    )

    right_column = w.Column(
        [
            text("select speed: "),
            drop_down(["slow", "medium", "fast"], key = "speed", enable_events = True)
        ]
    )

    connection_row = [w.Frame("Connection", [[left_column, right_column]], size = (600, 150))]

    search_row = [w.Frame("Search", [user_input("Keyword", push = False, key = "keyword"), button(SEARCH_BUTTON_LABEL) ], size = (600, 250))]

    command_row = [w.Frame("FTP", [user_input("Enter Command", key = "command", push = False), button(COMMAND_BUTTON_LABEL) ], size = (600, 250))]

    layout = [
        horizontal_line(),
        connection_row,
        horizontal_line(),
        search_row,
        # box with current users
        horizontal_line(),
        command_row
        # box with command history

    ]

    return w.Window(title, layout, size = WINDOW_SIZE, background_color = '#FFF1DB')
