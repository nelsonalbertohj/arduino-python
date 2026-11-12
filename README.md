# Arduino with Python

Run a Python script that reads a potentiometer, dims an LED and plots the
readings live, through an Arduino. Works on Windows and macOS. Allow about
30 minutes the first time.

## What you need

- An Arduino Uno or Nano and a USB cable that carries **data** (some only charge)
- A 10 kΩ potentiometer, an LED and a 220–330 Ω resistor
- **Wiring:** potentiometer outer legs to 5V and GND, middle leg to **A0**.
  Pin **9** → resistor → LED long leg; LED short leg → GND

## 1. Install Python

Download Python from [python.org/downloads](https://www.python.org/downloads/)
and run the installer.

- **Windows:** on the first screen, tick **Add python.exe to PATH**, then click Install Now.
- **macOS:** when it finishes, double-click **Install Certificates.command** in the window that opens.

Check it worked. Open **PowerShell** (Windows) or **Terminal** (macOS) and type:

| Windows | macOS |
| --- | --- |
| `py --version` | `python3 --version` |

It should print Python 3.10 or newer.

## 2. Prepare the board (once)

1. Install the [Arduino IDE](https://www.arduino.cc/en/software) and plug in the board.
2. **Tools → Board:** pick your board. Nano clones also need
   **Tools → Processor → ATmega328P (Old Bootloader)**.
3. **Tools → Port:** pick your board, and note its name
   (`COM3` on Windows, `/dev/cu.usbmodem…` on macOS).
4. **File → Examples → Firmata → StandardFirmata**, then click **Upload** and
   wait for **"Done uploading"**.
5. Close the Arduino IDE. Only one program can use the board at a time.

No port listed? Try another cable. Clone boards on Windows may need the
[CH340 driver](https://www.wch-ic.com/downloads/CH341SER_EXE.html).

## 3. Get the project and set it up (once)

1. On this page, click the green **Code** button → **Download ZIP**.
2. Unzip it, rename the folder to `arduino_workshop_mit`, and move it into
   your **Documents** folder.
3. In your terminal, run these lines:

**Windows**

```powershell
cd $HOME\Documents\arduino_workshop_mit
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

**macOS**

```bash
cd ~/Documents/arduino_workshop_mit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

This creates a `.venv` folder holding the three packages the script needs.

## 4. Run

In the project folder:

| Windows | macOS |
| --- | --- |
| `py potentiometer_led.py` | `python3 potentiometer_led.py` |

Turn the potentiometer: the LED dims and brightens, the numbers print, and a
window plots the last 10 seconds. Close the window or press **Ctrl+C** to stop.

If the board isn't found, add the port name from step 2, e.g.
`py potentiometer_led.py COM3`.

## How it works

- **StandardFirmata** lets Python use the board's pins over USB. The script does the rest.
- **The `.venv` folder** keeps the packages for this project only. The script
  switches to it by itself, so you never need to "activate" it.
- **Settings** sit at the top of the script: the pins, `SHOW_PLOT`
  (set `False` for no plot) and `PLOT_SECONDS`.
- **Activating also works**, as most Python projects expect:
  `.venv\Scripts\activate` in Command Prompt, or `source .venv/bin/activate`
  on macOS, then `python potentiometer_led.py`.
- **Arduino-only version:** `potentiometer_led_sketch/` does the same job with
  no Python. Upload it from the Arduino IDE (it replaces StandardFirmata).

## Troubleshooting

| Message | Fix |
| --- | --- |
| `py` or `python3` not recognized | Reinstall Python (Windows: tick **Add python.exe to PATH**), then open a new terminal |
| `A package is missing` | Do step 3 in the folder that holds the script |
| `can't open file` | `cd` into the project folder |
| `Could not find a serial port` | Plug the board in. Try another cable or the CH340 driver |
| `Resource busy` or `Access is denied` | Close the Arduino IDE |
| `not running StandardFirmata` | Upload StandardFirmata (step 2) and wait for "Done uploading". If the upload fails, see the next row |
| `Servo.h: No such file or directory` when uploading StandardFirmata | Arduino IDE: **Tools → Manage Libraries**, search **Servo**, click Install, then upload again |
| Upload error `not in sync` | Check board and port. Nano: try **Old Bootloader**. Unplug anything on pins 0 and 1 |
| `running scripts is disabled` | Activate in Command Prompt instead, or just run the file |

## Files

| File | What it is |
| --- | --- |
| `potentiometer_led.py` | The Python script |
| `requirements.txt` | The packages step 3 installs |
| `potentiometer_led_sketch/` | The same project as a plain Arduino sketch |
