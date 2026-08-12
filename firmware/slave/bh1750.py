from micropython import const
import time

# Endereço padrão I2C
BH1750_ADDR = const(0x23)

# Comandos
POWER_DOWN = const(0x00)
POWER_ON = const(0x01)
RESET = const(0x07)

# Modos de medição
CONTINUOUS_HIGH_RES_MODE = const(0x10)
CONTINUOUS_HIGH_RES_MODE_2 = const(0x11)
CONTINUOUS_LOW_RES_MODE = const(0x13)

ONE_TIME_HIGH_RES_MODE = const(0x20)
ONE_TIME_HIGH_RES_MODE_2 = const(0x21)
ONE_TIME_LOW_RES_MODE = const(0x23)


class BH1750:
    
    def __init__(self, i2c, addr=BH1750_ADDR):
        self.i2c = i2c
        self.addr = addr
        self.power_on()

    def _write(self, cmd):
        self.i2c.writeto(self.addr, bytearray([cmd]))

    def power_on(self):
        self._write(POWER_ON)

    def power_down(self):
        self._write(POWER_DOWN)

    def reset(self):
        self._write(RESET)

    def luminance(self, mode=CONTINUOUS_HIGH_RES_MODE):
        self._write(mode)

        if mode in (CONTINUOUS_HIGH_RES_MODE, CONTINUOUS_HIGH_RES_MODE_2,
                    ONE_TIME_HIGH_RES_MODE, ONE_TIME_HIGH_RES_MODE_2):
            time.sleep_ms(180)
        else:
            time.sleep_ms(24)

        data = self.i2c.readfrom(self.addr, 2)

        raw = (data[0] << 8) | data[1]
        lux = raw / 1.2

        return lux
