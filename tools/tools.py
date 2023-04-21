
from PySimpleGUI import Window
import PySimpleGUI as w

SEND_MESSAGE_END = '\r\n'
READ_MESSAGE_END = '\r\n\r\n'

'''
--
'''

CONNECT_BUTTON_LABEL = "Connect"
SEARCH_BUTTON_LABEL  = "Search"
COMMAND_BUTTON_LABEL = "Go"

WINDOW_SIZE = (600, 800)


'''
-- tool methods
'''

def log(message : str):
    print(f'[+] - {message}')


def error(message : str):
    print(f'[-] - {message}')

'''
-- window methods
'''

def text(label,  size = None, font = None, text_color = None):
    return [w.Text(label, text_color = text_color)]

def user_input(label, key, push = True, default_text = '', size = (30, 1)):
    return  [w.Text(f"{label}:"), w.Push(), w.InputText(key = key, size = size)] if push == True else [w.Text(f"{label} :"), w.InputText(key = key, size = size)]

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

def add_table_row(data):
    return [w.Table(values = data, headings = ["Speed", "Hostname", "Filename"], num_rows = 10, justification = "center", key = "table", col_widths = [(100, True), (100, True), (100, True)])]

def user_output(key, size = (600, 10)):
    return [w.Output(size = size, key = key)]

'''
-- top-level window method
'''

def open_window(title : str) -> Window:

    left_column = w.Column(
        [
            user_input("Hostname", key = "hostname"),
            user_input("Port", key = "port"),
            button(CONNECT_BUTTON_LABEL, bind = True)
        ]
    )

    right_column = w.Column(
        [
            user_input("Username", key = "username"),
            text("Speed"),
            drop_down(["slow", "medium", "fast"], key = "speed", enable_events = True)
        ]
    )

    connection_frame = [w.Frame("Connection", [[left_column, right_column]], size = (600, 150))]

    search_frame = [
        w.Frame("Search",
        [
            user_input("Keyword", push = False, key = "keyword"),
            button(SEARCH_BUTTON_LABEL),
            add_table_row([["test", "test", "test"]])
        ],
        size = (600, 250))
    ]

    command_frame = [
        w.Frame("FTP",
        [
            user_input("Enter Command", key = "command", push = False),
            button(COMMAND_BUTTON_LABEL),
            user_output("output")
            # w.Output(size = (60, 10), key = "output")
        ],
        size = (600, 250))
    ]

    layout = [
        horizontal_line(),
        connection_frame,
        horizontal_line(),
        search_frame,
        horizontal_line(),
        command_frame
    ]

    return w.Window(title, layout, size = WINDOW_SIZE, background_color = '#FFF1DB')
