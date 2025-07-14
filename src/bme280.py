# bme280.py (versão simplificada e funcional para MicroPython)
import ustruct

class BME280:
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.address = address
        self._ctrl_meas = b'\x27'
        self._ctrl_hum = b'\x01'
        self._config = b'\xA0'
        self._reg_data = 0xF7
        self._load_calibration()

        self.i2c.writeto_mem(self.address, 0xF2, self._ctrl_hum)
        self.i2c.writeto_mem(self.address, 0xF4, self._ctrl_meas)
        self.i2c.writeto_mem(self.address, 0xF5, self._config)

    def _read(self, reg, length):
        return self.i2c.readfrom_mem(self.address, reg, length)

    def _load_calibration(self):
        calib = self._read(0x88, 26)
        hcalib = self._read(0xE1, 7)

        self.dig_T1 = ustruct.unpack('<H', calib[0:2])[0]
        self.dig_T2 = ustruct.unpack('<h', calib[2:4])[0]
        self.dig_T3 = ustruct.unpack('<h', calib[4:6])[0]
        self.dig_H1 = self._read(0xA1, 1)[0]
        self.dig_H2 = ustruct.unpack('<h', hcalib[0:2])[0]
        self.dig_H3 = hcalib[2]
        self.dig_H4 = (hcalib[3] << 4) | (hcalib[4] & 0x0F)
        self.dig_H5 = (hcalib[5] << 4) | (hcalib[4] >> 4)
        self.dig_H6 = ustruct.unpack('b', hcalib[6:7])[0]
        self.dig_P1 = ustruct.unpack('<H', calib[6:8])[0]
        self.dig_P2 = ustruct.unpack('<h', calib[8:10])[0]
        self.dig_P3 = ustruct.unpack('<h', calib[10:12])[0]
        self.dig_P4 = ustruct.unpack('<h', calib[12:14])[0]
        self.dig_P5 = ustruct.unpack('<h', calib[14:16])[0]
        self.dig_P6 = ustruct.unpack('<h', calib[16:18])[0]
        self.dig_P7 = ustruct.unpack('<h', calib[18:20])[0]
        self.dig_P8 = ustruct.unpack('<h', calib[20:22])[0]
        self.dig_P9 = ustruct.unpack('<h', calib[22:24])[0]

    def read_compensated_data(self):
        data = self._read(self._reg_data, 8)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (self._read(0xFD, 2)[0] << 8) | self._read(0xFD, 2)[1]

        var1 = (((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        temperature = ((t_fine * 5 + 128) >> 8) / 100

        h = t_fine - 76800.0
        humidity = adc_h - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * h)
        humidity = humidity * (self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * h * (1.0 + self.dig_H3 / 67108864.0 * h)))
        humidity = humidity * (1.0 - self.dig_H1 * humidity / 524288.0)
        humidity = max(0, min(humidity, 100))  # clamp to [0,100]

        # Pressure
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = var2 / 4.0 + self.dig_P4 * 65536.0
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1

        if var1 == 0:
            pressure = 0  # avoid division by zero
        else:
            pressure = 1048576.0 - adc_p
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = self.dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * self.dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + self.dig_P7) / 16.0
            pressure = pressure / 100.0  # Convert to hPa


        return temperature, pressure, humidity
