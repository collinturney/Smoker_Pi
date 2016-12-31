#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import time
import logging
import Adafruit_MAX31855.MAX31855 as MAX31855
import RPi.GPIO as gpio


class Sensor(object):

    def __init__(self, **kwargs):
        CLK_PIN = kwargs.get("CLK_PIN", 25)
        CS_PIN  = kwargs.get("CS_PIN",  24)
        DO_PIN  = kwargs.get("DO_PIN",  18)
        self.sensor = MAX31855.MAX31855(CLK_PIN, CS_PIN, DO_PIN)

    def internal_temp(self):
        temp = self.sensor.readInternalC()
        return Sensor.c_to_f(temp)

    def thermo_temp(self):
        temp = self.sensor.readTempC()
        return Sensor.c_to_f(temp)

    @staticmethod
    def c_to_f(c):
        return c * (9.0 / 5.0) + 32


class Heater(object):

    def __init__(self, **kwargs):
        self.PWR_PIN = kwargs.get("PWR_PIN", 23)
        self.throttle_seconds = kwargs.get("throttle_seconds", 20)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.PWR_PIN, gpio.OUT)
        gpio.output(self.PWR_PIN, False)
        self.poweron = False
        self.last_toggle = None

    def is_on(self):
        return self.poweron

    def is_off(self):
        return not self.poweron

    def turn_on(self):
        if self.is_throttled() or self.is_on():
            return False
        
        self.last_toggle = time.time()
        gpio.output(self.PWR_PIN, True)
        self.poweron = True

        return True

    def turn_off(self):
        if self.is_throttled() or self.is_off():
            return False

        self.last_toggle = time.time()
        gpio.output(self.PWR_PIN, False)
        self.poweron = False

        return True

    def is_throttled(self):
        if not self.last_toggle:
            return False

        return (time.time() - self.last_toggle) < self.throttle_seconds


class Thermostat(object):

    def __init__(self, sensor, heater):
        self.sensor = sensor
        self.heater = heater

        log_file = time.strftime("smokelog_%Y%m%d-%H%M%S.csv")
        logging.basicConfig(format="%(message)s", filename=log_file, level=logging.INFO)

    def set(self, set_temp):
        self.set_temp = set_temp

    def threshold(self, threshold):
        self.threshold = threshold

    def log_temps(self, internal, thermo):
        print("%s - internal=%.2f thermo=%.2f" % (time.ctime(), internal, thermo))

        message = "%d,%.2f,%.2f,%d,%d" % (int(time.time()), internal, thermo, self.heater.is_throttled(), self.heater.is_on())
        logging.info(message)


    def control_loop(self):
        while True:
            internal_temp = self.sensor.internal_temp()
            thermo_temp = self.sensor.thermo_temp()

            self.log_temps(internal_temp, thermo_temp)

            if thermo_temp < self.set_temp and self.heater.is_off():
                print("Turning on heater!")
                self.heater.turn_on()
                
            elif thermo_temp > self.set_temp and self.heater.is_on():
                print("Turning off heater!")
                self.heater.turn_off()

            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()

    def configure():
        parser.add_argument('-s', '--set-temp', type=int, default=215)
        return parser.parse_args()

    args = configure()

    sensor = Sensor()
    heater = Heater()

    thermostat = Thermostat(sensor, heater)
    thermostat.set(args.set_temp)
    thermostat.control_loop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
