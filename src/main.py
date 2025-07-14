from machine import I2C, Pin
from time import sleep
import bme280
import bh1750

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
# sensor_bme280 = bme280.BME280(i2c)
# sensor_bh1750 = bh1750.BH1750(i2c)

while True:
    bme = bme280.BME280(i2c)
    bh  = bh1750.BH1750(i2c)
    temp, press, hum = bme.read_compensated_data()
    lum = bh.luminance()
    print(f"{temp:.2f} °C\t{press:.2f} hPa\t{hum:.2f} %\t{lum:.2f} lux")
    sleep(5)
