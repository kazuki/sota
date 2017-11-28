Sota unofficial library
=======================

[Sota](https://sota.vstone.co.jp/home/)君(Intel Edison版)を
謎のサービスを経由せずに自由な方法で制御します。

straceを使って解析しましたが、
組み込みとかI2C等の知識がないので、
正しくない制御をしているかも知れません。

機能
----

* LED制御 (右目・左目)
* サーボ制御 (1番〜8番)

Python Library
--------------

```python
import time
from sota import Sota, SotaLED

sota = Sota()

# 右目を赤色、左目を青色、口を光らせる
sota.set_led(SotaLED.Right, (0xff, 0x00, 0x00))
sota.set_led(SotaLED.Left, (0x00, 0x00, 0xff))
sota.set_led(SotaLED.Mouth, 0xff)

# サーボONにし初期位置に移動
sota.servo_on()

# 体を左右に回転
sota.set_servo({1: 1200})
time.sleep(1)
sota.set_servo({1: -1200})
time.sleep(1)
sota.set_servo({1: 0})
time.sleep(1)

# サーボOFF / LED OFF
sota.servo_off()
sota.set_led(SotaLED.Right, (0x00, 0x00, 0x00))
sota.set_led(SotaLED.Left, (0x00, 0x00, 0x00))
sota.set_led(SotaLED.Mouth, 0x00)
```
