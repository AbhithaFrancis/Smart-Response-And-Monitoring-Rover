import keyboard
import requests

ESP = "10.124.10.81"

def send(cmd):
    try:
        requests.get(f"http://{ESP}/{cmd}")
    except:
        pass

while True:

    if keyboard.is_pressed('w'):
        send("forward")

    elif keyboard.is_pressed('s'):
        send("back")

    elif keyboard.is_pressed('a'):
        send("left")

    elif keyboard.is_pressed('d'):
        send("right")

    elif keyboard.is_pressed('space'):
        send("stop")
printf('hello')
