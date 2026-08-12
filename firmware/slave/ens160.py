from machine import I2C
import time

ENS160_ADDR = 0x53

class ENS160:

    def __init__(self, i2c, addr=ENS160_ADDR):
        self.i2c = i2c
        self.addr = addr

        # reset
        self.i2c.writeto_mem(self.addr, 0x10, b'\xF0')
        time.sleep_ms(100)

        # modo operação
        self.i2c.writeto_mem(self.addr, 0x10, b'\x02')
        time.sleep_ms(100)

    def get_data(self):

        data = self.i2c.readfrom_mem(self.addr, 0x22, 6)

        tvoc = data[0] | (data[1] << 8)
        eco2 = data[2] | (data[3] << 8)

        aqi = self.i2c.readfrom_mem(self.addr, 0x21, 1)[0]

        return {
            "TVOC": tvoc,
            "eCO2": eco2,
            "AQI": aqi
        }
