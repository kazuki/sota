import os
import fcntl
import struct


I2C_SLAVE = 0x0703


class Sota(object):
    def __init__(self):
        self._i2c = os.open('/dev/i2c-1', os.O_RDWR)
        self._tty = os.open('/dev/ttyMFD1', os.O_RDWR)
        fcntl.ioctl(self._i2c, I2C_SLAVE, 5)

    def __del__(self):
        if self._i2c > 0:
            os.close(self._i2c)
            self._i2c = 0
        if self._tty > 0:
            os.close(self._tty)
            self._tty = 0

    def set_led(self, led, color):
        if led == SotaLED.Mouth:
            if isinstance(color, int):
                if color < 0 or color > 255:
                    raise ValueError('invalid color range')
            else:
                raise ValueError('invalid color type')
            b = bytearray(2)
            b[0] = 0x08
            b[1] = color
            os.write(self._i2c, b)
            return
        if isinstance(color, int):
            rgb = ((color >> 16) & 0xff,
                   (color >> 8) & 0xff,
                   color & 0xff)
        elif isinstance(color, tuple):
            if (len(color) != 3 or (color[0] < 0 or color[0] > 255) or
                    (color[1] < 0 or color[1] > 255) or
                    (color[2] < 0 or color[2] > 255)):
                raise ValueError('invalid color range')
            rgb = color
        else:
            raise ValueError('invalid color type')
        if led == SotaLED.Left:
            addr = 0x02
        elif led == SotaLED.Right:
            addr = 0x05
        else:
            raise ValueError('invalid led type')
        b = bytearray(2)
        for i, c in enumerate(rgb):
            b[0] = addr + i
            b[1] = c
            os.write(self._i2c, b)

    def servo_on(self):
        self.set_servo({
            1: 0, 2: -795, 3: 0, 4: 795, 5: 0, 6: 0, 7: 0, 8: 0})

    def servo_off(self):
        self.set_servo({
            1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}, power=False)

    def get_servo_angle(self, servo_id):
        b = bytearray(8)
        b[0:8] = '\xfa\xaf\x00\x0f\x2a\x02\x00\x00'
        b[2] = servo_id
        b[-1] = self._checksum(b[2:-1])
        os.write(self._tty, b)
        os.read(self._tty, 8)
        res = os.read(self._tty, 1024)
        return struct.unpack('<h', res[7:9])

    def _checksum(self, X):
        c = 0
        for x in X:
            c ^= x
        return c

    def set_servo(self, angles, power=True):
        if len(angles) > 8:
            raise ValueError('invalid angles length')
        b0 = bytearray(32)
        b0[0:6] = '\xfa\xaf\x00\x00\x23\x03'
        b0[6] = len(angles)
        for i, servo_id in enumerate(angles.keys()):
            off = 7 + i * 3
            b0[off] = servo_id
            if power:
                b0[off + 1] = 0x64
                b0[off + 2] = 0x01
            else:
                b0[off + 1] = 0x00
                b0[off + 2] = 0x00
        b0 = b0[0:8 + len(angles) * 3]
        b0[-1] = self._checksum(b0[2:-1])

        b1 = bytearray(32)
        b1[0:6] = '\xfa\xaf\x00\x00\x1e\x03'
        b1[6] = len(angles)
        for i, servo_id in enumerate(angles.keys()):
            off = 7 + i * 3
            b1[off] = servo_id
            b1[off+1:off+3] = struct.pack('<h', angles[servo_id])
        b1 = b1[0:8 + len(angles) * 3]
        b1[-1] = self._checksum(b1[2:-1])
        msg = b0 + b1
        os.write(self._tty, msg)
        os.read(self._tty, 1024)


class SotaLED(object):
    Left = 0
    Right = 1
    Mouth = 2
