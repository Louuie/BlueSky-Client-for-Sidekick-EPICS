# Elias Dandouch
# Summer SURF 2025 RESEARCH (06/26/25)
# ------------------------------------
# SIMULATION VERSION (no EPICS IOC required)
# Uses ophyd.sim.Signal instead of EpicsSignal so plans can run offline.

import datetime
import csv
from ophyd import Device, Component as Cpt
from ophyd.sim import Signal  # <-- simulation-friendly signal type
from bluesky import RunEngine
from bluesky.plan_stubs import mv, sleep
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.plans import scan


# Device Definitions (Simulation Mode)
class Shutter(Device):
    enable = Cpt(Signal, value=0)      # Simulated PV
    duration = Cpt(Signal, value=0.0)  # Simulated PV

class LEDs(Device):
    ch0_brig = Cpt(Signal, value=0)
    ch0_dur = Cpt(Signal, value=0.0)
    debug = Cpt(Signal, value=0)
    info = Cpt(Signal, value=0)


# Instantiate Devices
shutter = Shutter(name="shutter")
leds = LEDs(name="leds")


# Bluesky RunEngine Setup
RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)
print("Running in SIMULATION MODE (no EPICS hardware connected).")


# LED + Shutter Test Plan
def leds_shutter_test_plan():
    print("Starting LED + Shutter test (simulated)...")

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

    print("Test complete (simulated).")


# LED Brightness Scan (Regular Bluesky scan)
def led_brightness_scan():
    print("Running LED brightness scan (simulated)...")

    # Metadata for record-keeping
    RE.md['run_start_time'] = datetime.datetime.now().isoformat()
    RE.md['operator'] = "Elias Dandouch"
    RE.md['experiment'] = "Sidekick LED Brightness Sweep (Simulated)"

    # Sweep LED brightness 0 → 255 in 6 steps
    yield from scan([leds.ch0_brig], leds.ch0_brig, 0, 255, 6)

    # Turn off LED after scan
    yield from mv(leds.ch0_brig, 0)
    print("Scan complete (simulated).")


# LED Action List Scan (List/Action Scan)
def led_action_scan(filename="led_action_list.csv"):
    print(f"Running LED Action Scan from CSV (simulated): {filename}")

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
    RE.md['experiment'] = "Sidekick LED Action Scan (Simulated)"
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
    print("Action scan complete (simulated).")


if __name__ == "__main__":
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
