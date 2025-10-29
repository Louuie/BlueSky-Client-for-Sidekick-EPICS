# Elias Dandouch
# Summer SURF 2025 RESEARCH (06/26/25)
from ophyd import EpicsSignal, Device, Component as Cpt
from bluesky import RunEngine
from bluesky.plan_stubs import mv, sleep
from bluesky.callbacks import BestEffortCallback
from bluesky.plans import scan
import datetime
import csv

# Device Definitions
# More can be found here: https://sfeister.github.io/sidekick-epics-docs/model1/model1-process-variables/
class Shutter(Device):
    enable = Cpt(EpicsSignal, "SHUTTER:enable")
    duration = Cpt(EpicsSignal, "SHUTTER:DURation")

class LEDs(Device):
    ch0_brig = Cpt(EpicsSignal, "LEDS:CH0:brig")
    ch0_dur = Cpt(EpicsSignal, "LEDS:CH0:dur")
    debug = Cpt(EpicsSignal, "LEDS:debug")
    info = Cpt(EpicsSignal, "LEDS:info")

# Instantiate Devices
shutter = Shutter(name="shutter")
leds = LEDs(name="leds")

# Bluesky RunEngine Setup
RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)  # Live table + plotting

# LED + Shutter Test Plan
def leds_shutter_test_plan():
    print("Starting LED + Shutter test...")

    # Turn on LED channel 0
    yield from mv(leds.ch0_brig, 128)
    yield from sleep(0.5)

    # Open shutter
    yield from mv(shutter.enable, 1)
    yield from sleep(1)

    # Close shutter
    yield from mv(shutter.enable, 0)

    # Turn off LED
    yield from mv(leds.ch0_brig, 0)

    print("Test complete.")

# LED Brightness Scan (Regular Bluesky scan) - I'm keeping this here just in-case we may need it later down the road in this test plan
def led_brightness_scan():
    print("Running LED brightness scan...")

    # Metadata for record-keeping
    RE.md['run_start_time'] = datetime.datetime.now().isoformat()
    RE.md['operator'] = "Elias Dandouch"
    RE.md['experiment'] = "Sidekick LED Brightness Sweep"

    # Sweep LED brightness 0 → 255 in 6 steps
    yield from scan([leds.ch0_brig], leds.ch0_brig, 0, 255, 6)

    # Turn off LED after scan
    yield from mv(leds.ch0_brig, 0)
    print("Scan complete. Data saved in RunEngine memory/log.")

# LED Action List Scan (List/Action Scan)
def led_action_scan(filename="led_action_list.csv"):
    print(f"Running LED Action Scan from predefined CSV we made: {filename}")

    try:
        with open(filename) as f:
            reader = csv.DictReader(f)
            steps = list(reader)
    except FileNotFoundError:
        print(f"ERROR: File '{filename}' not found.")
        return

    if not steps:
        print("ERROR: No steps found in CSV file.")
        return

    # Metadata
    RE.md['run_start_time'] = datetime.datetime.now().isoformat()
    RE.md['operator'] = "Elias Dandouch"
    RE.md['experiment'] = "Sidekick LED Action Scan"
    RE.md['action_list_file'] = filename

    for i, row in enumerate(steps, start=1):
        try:
            b = float(row["brightness"])
            dur = float(row["duration"])
            s = int(row["shutter"])
        except (KeyError, ValueError):
            print(f"Skipping invalid row {i}: {row}")
            continue

        print(f"Step {i}: LED={b}, Duration={dur}s, Shutter={s}")
        yield from mv(leds.ch0_brig, b)
        yield from mv(shutter.enable, s)
        yield from sleep(dur)

    # Turn off LED + close shutter after sequence
    yield from mv(leds.ch0_brig, 0)
    yield from mv(shutter.enable, 0)
    print("Action scan complete.")

if __name__ == "__main__":
    # Creating a user argument options for testing purposes, I'll prob get rid of this later down the road
    print("Options:")
    print("1. LED + Shutter Test")
    print("2. LED Brightness Scan (0–255 sweep)")
    print("3. LED Action Scan (List/Action from CSV)\n")

    choice = input("Select (1, 2, or 3): ").strip()

    if choice == "1":
        RE(leds_shutter_test_plan())
    elif choice == "2":
        RE(led_brightness_scan())
    elif choice == "3":
        filename = input("Enter CSV filename (default: led_action_list.csv): ").strip() or "led_action_list.csv"
        RE(led_action_scan(filename))
    else:
        print("Invalid choice. Exiting.")
