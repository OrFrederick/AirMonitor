# https://github.com/gilyes/pi-shutdown/blob/master/pishutdown.py
import RPi.GPIO as GPIO
from subprocess import call
from datetime import datetime
import config as cfg

# pushbutton connected to this GPIO pin, using pin 5 also has the benefit of
# waking / powering up Raspberry Pi when button is pressed
shutdownPin = cfg.SHUTDOWN_BTN

# if button pressed for at least this long then shut down. if less then reboot.
shutdownMinSeconds = 1

# button debounce time in seconds
debounceSeconds = 0.01

# Number after GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(shutdownPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

buttonPressedTime = None


def buttonStateChanged(pin):
    global buttonPressedTime

    if not (GPIO.input(pin)):
        # button is down
        if buttonPressedTime is None:
            buttonPressedTime = datetime.now()
    else:
        # button is up
        if buttonPressedTime is not None:
            elapsed = (datetime.now() - buttonPressedTime).total_seconds()
            buttonPressedTime = None
            if elapsed >= shutdownMinSeconds:
                # button pressed for more than specified time, shutdown
                call(['sudo', 'shutdown', '-h', 'now'], shell=False)
            elif elapsed >= debounceSeconds:
                # button pressed for a shorter time, reboot
                call(['sudo', 'shutdown', '-r', 'now'], shell=False)


# subscribe to button presses
GPIO.add_event_detect(shutdownPin, GPIO.BOTH, callback=buttonStateChanged)
