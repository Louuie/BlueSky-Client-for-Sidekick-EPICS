# Elias Dandouch
# Summer SURF 2025 RESEARCH (06/26/25)

from ophyd import EpicsSignal, Device, Component as Cpt
from bluesky import RunEngine
from bluesky.plan_stubs import mv, sleep
import asyncio

# Device Definitions
# More can be found here: https://sfeister.github.io/sidekick-epics-docs/model1/model1-process-variables/

class Shutter(Device):
    enable = Cpt(EpicsSignal, "SHUTTER:enable")
    duration = Cpt(EpicsSignal, "SHUTTER:DURation")

class LEDs(Device):
    ch0_brig = Cpt(EpicsSignal, "LEDS:CH0:brig")
    ch1_brig = Cpt(EpicsSignal, "LEDS:CH1:brig")
    ch2_brig = Cpt(EpicsSignal, "LEDS:CH2:brig")
    ch3_brig = Cpt(EpicsSignal, "LEDS:CH3:brig")
    ch4_brig = Cpt(EpicsSignal, "LEDS:CH4:brig")
    ch5_brig = Cpt(EpicsSignal, "LEDS:CH5:brig")
    
    ch0_dur = Cpt(EpicsSignal, "LEDS:CH0:dur")
    ch1_dur = Cpt(EpicsSignal, "LEDS:CH1:dur")
    ch2_dur = Cpt(EpicsSignal, "LEDS:CH2:dur")
    ch3_dur = Cpt(EpicsSignal, "LEDS:CH3:dur")
    ch4_dur = Cpt(EpicsSignal, "LEDS:CH4:dur")
    ch5_dur = Cpt(EpicsSignal, "LEDS:CH5:dur")

    debug = Cpt(EpicsSignal, "LEDS:debug")
    info = Cpt(EpicsSignal, "LEDS:info")

# Devices

shutter = Shutter(name="shutter")
leds = LEDs(name="leds")

# Bluesky RunEngine

RE = RunEngine({})

# Example Plan

def leds_shutter_test_plan():
    # Turn on LED channel 0
    yield from mv(leds.ch0_brig, 128)
    yield from sleep(0.5)

    # Open shutter
    yield from mv(shutter.enable, 1)
    yield from sleep(1)

    # Close shutter
    yield from mv(shutter.enable, 0)

    # Turn off LED channel 0
    yield from mv(leds.ch0_brig, 0)

# Run it

if __name__ == "__main__":
    RE(leds_shutter_test_plan())
