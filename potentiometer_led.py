"""
Turn a potentiometer to change an LED's brightness, using Python.

This does the same job as the Arduino sketch, but the "thinking" happens on
your computer. The Arduino just runs StandardFirmata, a ready-made sketch that
lets Python read and set its pins over the USB cable.

How to run it (in a terminal, inside this folder):
    Windows:  py potentiometer_led.py
    macOS:    python3 potentiometer_led.py
If it cannot find the board, add the port name at the end, e.g.
    py potentiometer_led.py COM3
    python3 potentiometer_led.py /dev/cu.usbmodem2101
Press Ctrl+C to stop (or close the plot window, if it is open).
"""

import os
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

# ----------------------------------------------------------------------------
# Settings you can change
# ----------------------------------------------------------------------------
LED_PIN = 9          # The LED's pin. It must be a PWM pin (marked with ~ on the board).
POT_PIN = 0          # The potentiometer's pin: 0 means A0.
READ_EVERY_MS = 50   # How often to read the potentiometer, in milliseconds.
SHOW_PLOT = True     # True = also open a live plot window. False = numbers only.
PLOT_SECONDS = 10    # How many seconds of readings the plot shows at once.

# ----------------------------------------------------------------------------
# Step 1: Use the project's own Python
# ----------------------------------------------------------------------------
# The extra packages this script needs live in the ".venv" folder next to it.
# If you started the script with your computer's normal Python, we simply
# start it again using the Python inside .venv. That is why you never have to
# "activate" anything: running the file is enough.
if "__file__" not in globals():
    # This happens when the code is run line by line (VS Code: Shift+Enter, or
    # "Run in Interactive Window") instead of as a whole file.
    sys.exit("Run this script as a whole file: in VS Code, click the Run Python File "
             "button (the triangle at the top right), or type "
             "'python3 potentiometer_led.py' in a terminal.")
folder = Path(__file__).resolve().parent
venv_folder = folder / ".venv"
if os.name == "nt":                                   # Windows
    venv_python = venv_folder / "Scripts" / "python.exe"
else:                                                 # macOS and Linux
    venv_python = venv_folder / "bin" / "python"

already_in_venv = Path(sys.prefix).resolve() == venv_folder.resolve()
if venv_python.exists() and not already_in_venv:
    try:
        # Run this same file again with the .venv's Python, passing on any port name.
        sys.exit(subprocess.call([str(venv_python), __file__, *sys.argv[1:]]))
    except KeyboardInterrupt:
        sys.exit(0)   # Ctrl+C also reaches the copy we started, and it cleans up.

# ----------------------------------------------------------------------------
# Step 2: Load the library that talks to the Arduino
# ----------------------------------------------------------------------------
try:
    from pyfirmata2 import Arduino
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
except ImportError as error:
    print(f"A package is missing ({error.name}). Set up the .venv folder first")
    print("(step 3 in README.md), then run this script again.")
    sys.exit(1)

# ----------------------------------------------------------------------------
# Step 3: Connect to the board
# ----------------------------------------------------------------------------
# A port name typed after the script's name is used; otherwise we search for one.
port = sys.argv[1] if len(sys.argv) > 1 else Arduino.AUTODETECT

print("Connecting to the board...", flush=True)
try:
    board = Arduino(port)
except Exception as error:
    print("Could not connect to the board:", error)
    print("Check that: the board is plugged in, the Arduino IDE is closed,")
    print("and StandardFirmata has been uploaded to the board.", flush=True)
    os._exit(1)   # Quit right away (this skips some noisy messages from the library).

# Make sure the board is really running StandardFirmata. A board still running
# another sketch also "connects", but sends text the library cannot understand,
# so the readings would be nonsense. We ask the board which program it runs and
# wait up to 3 seconds for an answer.
board.samplingOn(READ_EVERY_MS)   # start listening to the board
board.send_sysex(0x79, [])        # 0x79 = Firmata's "which firmware are you?" question
for _ in range(30):
    if board.firmware:            # filled in when StandardFirmata answers
        break
    time.sleep(0.1)
if not board.firmware:
    print("The board is connected, but it is not running StandardFirmata.")
    print("Upload it from the Arduino IDE (File > Examples > Firmata >")
    print("StandardFirmata), close the IDE, and run this script again.", flush=True)
    os._exit(1)

print("Connected on", board.sp.port, "running", board.firmware)
print("Turn the potentiometer. To stop, close the plot window or press Ctrl+C.")

led = board.get_pin(f"d:{LED_PIN}:p")   # "d" = digital pin, "p" = PWM (brightness)
pot = board.analog[POT_PIN]             # the analog input the potentiometer is on

# ----------------------------------------------------------------------------
# Step 4: React to every new reading
# ----------------------------------------------------------------------------
# Recent readings are kept here for the plot, as (seconds, value) pairs.
# A deque with a maxlen drops the oldest reading when a new one arrives,
# so it always holds just the last PLOT_SECONDS seconds.
recent = deque(maxlen=PLOT_SECONDS * 1000 // READ_EVERY_MS)
start_time = time.time()


# The library calls this function each time a new potentiometer value arrives.
# It gives the value as a number from 0.0 to 1.0 (not 0-1023), and the LED
# also takes 0.0 to 1.0 (not 0-255), so we can pass it straight through.
def on_new_reading(value):
    if value is None:          # The very first reading can be empty; skip it.
        return
    led.write(value)           # Same as analogWrite(9, ...) in the sketch.

    # Print the numbers the Arduino sketch would have shown.
    pot_value = round(value * 1023)   # like analogRead(): 0-1023
    led_value = round(value * 255)    # like analogWrite(): 0-255
    print(f"pot={pot_value:4d}  led={led_value:3d}")

    recent.append((time.time() - start_time, pot_value))   # save it for the plot


# ----------------------------------------------------------------------------
# The live plot (optional: see SHOW_PLOT at the top)
# ----------------------------------------------------------------------------
# Opens a window and redraws the recent readings 20 times a second.
# It only *reads* the list above, so the LED keeps working exactly as before.
def live_plot():
    figure, axes = plt.subplots()
    line, = axes.plot([], [])                  # an empty line; we fill it in below
    axes.set_ylim(0, 1023)                      # the full analogRead() range
    axes.set_xlabel("Time (seconds)")
    axes.set_ylabel("Potentiometer (0-1023)")
    axes.set_title("Live potentiometer reading")

    def redraw(frame):
        if not recent:
            return line,
        times, values = zip(*list(recent))     # split the pairs into two lists
        line.set_data(times, values)
        newest = times[-1]
        axes.set_xlim(max(0, newest - PLOT_SECONDS), max(PLOT_SECONDS, newest))
        return line,

    # FuncAnimation calls redraw() every 50 ms. Keep it in a variable,
    # or Python throws it away and the plot stops moving.
    animation = FuncAnimation(figure, redraw, interval=50, cache_frame_data=False)
    plt.show()                                  # waits here until the window is closed


pot.register_callback(on_new_reading)   # call our function with each reading
pot.enable_reporting()                  # start sending readings

# ----------------------------------------------------------------------------
# Step 5: Keep running until you stop it, then tidy up
# ----------------------------------------------------------------------------
try:
    if SHOW_PLOT:
        live_plot()            # Runs until you close the plot window.
    else:
        while True:
            time.sleep(1)      # The work happens in on_new_reading; we just wait.
except KeyboardInterrupt:
    print("\nStopping.")
finally:
    led.write(0)               # Turn the LED off.
    board.exit()               # Close the connection so other programs can use the board.
