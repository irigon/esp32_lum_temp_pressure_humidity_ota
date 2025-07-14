# bh1750.py
import time

PWR_DOWN = 0x00
PWR_ON = 0x01
RESET = 0x07

CONT_HIRES_MODE = 0x10  # modo padrão (1 lx resolução)

class BH1750:
    def __init__(self, i2c, address=0x23):
        self.i2c = i2c
        self.address = address
        self.i2c.writeto(self.address, bytearray([PWR_ON]))
        self.i2c.writeto(self.address, bytearray([RESET]))
        self.mode = CONT_HIRES_MODE

    def luminance(self, mode=None):
        if mode is None:
            mode = self.mode
        self.i2c.writeto(self.address, bytearray([mode]))
        time.sleep_ms(180)
        data = self.i2c.readfrom(self.address, 2)
        result = (data[0] << 8) | data[1]
        return result / 1.2  # conversão para lux
