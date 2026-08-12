from machine import I2C
import time

class AHT21:

    def __init__(self, i2c, addr=0x38):
        self.i2c = i2c
        self.addr = addr

        if addr not in i2c.scan():
            raise OSError("AHT21 not found")

        self.i2c.writeto(addr, b'\xBE\x08\x00')
        time.sleep_ms(10)

    def measure(self):
        self.i2c.writeto(self.addr, b'\xAC\x33\x00')
        time.sleep_ms(80)

        data = self.i2c.readfrom(self.addr, 6)

        raw_h = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        raw_t = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]

        humidity = raw_h * 100 / 1048576
        temperature = raw_t * 200 / 1048576 - 50

        return temperature, humidity
