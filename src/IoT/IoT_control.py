import os, time

import RPi.GPIO as GPIO
import Adafruit_DHT as dht
from gpiozero import MotionSensor
from gpiozero import MCP3008


class IoTController(object):
    # initial
    def __init__(self):
        self.send_freq: int = 3  # sec

        self.DHT_PIN: int = 4
        self.MOTION_PIN: int = 21
        self.LIGHT_PIN: int = 0
        self.INDOOR_LED_PIN: int = 12
        self.FAN_FIN: int = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INDOOR_LED_PIN, GPIO.OUT, initial=0)
        GPIO.setup(self.FAN_FIN, GPIO.OUT, initial=0)

    # Temp/Humi Sensor
    def get_DHT(self):
        hum, temp = dht.read_retry(dht.DHT11, self.DHT_PIN)
        return hum, temp

    # Motion sensor
    def get_PIR(self, timeout=None):
        if timeout is None:
            timeout = self.send_freq
        pir = MotionSensor(self.MOTION_PIN)
        move = pir.wait_for_motion(timeout=timeout)
        return move

    # Illumination sensor
    def get_illumi(self):
        light = MCP3008(self.LIGHT_PIN)
        # light.max_voltage=5.0
        lux = ((2 ** 10 * (5 - light.voltage) * 1) / 5) - 204
        # print("Light:{}".format(lux))
        return lux

    # indoor LED light
    def op_indoor_led(self, isON=False):
        if isON:
            GPIO.output(self.INDOOR_LED_PIN, 1)
        else:
            GPIO.output(self.INDOOR_LED_PIN, 0)

    # FAN motor
    def op_fan(self, isON=False):
        if isON:
            GPIO.output(self.FAN_FIN, 1)
        else:
            GPIO.output(self.FAN_FIN, 0)

    def recevice_data(self, i:int or None=None, isDebug:bool=False):
        strat_time = time.time()
        h, t = self.get_DHT()
        lux = self.get_illumi()
        motion = self.get_PIR()

        time_gap = self.send_freq - (time.time() - strat_time)
        time.sleep(time_gap) if time_gap > 0 else None
        print(f"{time.time()}, {t}*C, {h}%, {motion}, {lux}")

        if isDebug:
            # op_state = 0
            # if i % 3 == 0:
            #     if op_state == 0:
            #         op_state = 1
            #     else:
            #         op_state = 0
            #     self.op_indoor_led(isON=op_state)
            #     self.op_fan(isON=op_state)

            filename = 'receive_data'
            file_path = f'./{filename}_{i // 10000}.csv'

            try:
                if not os.path.exists(path=file_path):
                    with open(file_path, 'a') as f:
                        f.write('unix_timestamp, temperature(*C), humility(%), motion, illuminate(lux)\n')
                        print(f"Successfully created {file_path}")
            except OSError:
                raise OSError(f"Fail to create {file_path} !")

            with open(file_path, 'a') as f:
                f.write(f'{time.time()}, {t}, {h}, {motion}, {lux}\n')


# Data -> write receive_data.txt file
if __name__ == '__main__':
    iiot = IoTController()

    i = 1
    while True:
        iiot.recevice_data(i, isDebug=True)
        i += 1
