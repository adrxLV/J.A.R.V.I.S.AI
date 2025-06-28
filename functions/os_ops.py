import os
import subprocess as sp

paths = {
    'discord': "C:\\Users\\%user%\\AppData\\Local\\Discord\\app-1.0.9173\\Discord.exe",
    'calculator': "C:\\Windows\\System32\\calc.exe"
}

def open_camera():
    sp.run('start microsoft.windows.camera:', shell=True)

def open_notepad():
    sp.run('notepad.exe', shell=True)


def open_discord():
    os.startfile(paths['discord'])

def open_cmd():
    os.system('start cmd')

def open_calculator():
    sp.Popen(paths['calculator'])
def take_screenshot():
    print("screenshot functionality is not implemented yet.")
