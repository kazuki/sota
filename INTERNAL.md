# Edison版Sota君の制御方法

## LED制御

I2C Bus=1 Chip-Addr=5の以下のアドレスにRGB値を書き込むことで光らせる

* 右目: 0x02(R), 0x03(G), 0x04(B)
* 左目: 0x05(R), 0x06(G), 0x07(B)
* 口: 0x08(Brightness)

```
$ i2cset 1 5 0x02 0xff  # 右目を赤くする (0xFF0000)
$ i2cset 1 5 0x03 0xff  # 右目を黄色にする(0xFFFF00)
$ i2cset 1 5 0x02 0x00  # 右目を緑色にする (0x00FF00)
```

## サーボ制御

/dev/ttyMFD1 を使って制御。エコーありなので適宜readをかける。

checksumは3バイト以降の排他的論理和を計算。

### サーボの現在位置を取得(恐らく)

Request(8B. IDは1Bで1〜8の値が入る):

```
\xfa\xaf<ID>\x0f\x2a\x02\x00<CHECKSUM>
```

Response(10B. Valueは16bit-SignedInt-LE)

```
\xfd\xdf<ID>\x00\x2a\x02\x01<Value><CHECKSUM>
```

### サーボOFF

基本的には8個全部を一度にOFFにする。
一行目はサーボ1〜8に関して指定。
2行目は初期位置を指定している。不要かもしれない？

```
\xfa\xaf\x00\x00\x23\x03<対象サーボ数(1B)><サーボID_1(1B)>\x00\x00...<サーボID_N(1B)>\x00\x00<CHECKSUM>
\xfa\xaf\x00\x00\x1e\x03\x08\x01\x00\x00\x02\xe5\xfc\x03\x00\x00\x04\x1b\x03\x05\x00\x00\x06\x00\x00\x07\x00\x00\x08\x00\x00\x1c
```

### サーボON + サーボ位置指定

1個以上のサーボ位置を指定。

```
\xfa\xaf\x00\x00\x23\x03<対象サーボ数(1B)><サーボID_1(1B)>\x64\x01...<サーボID_N(1B)>\x64\x01<CHECKSUM>
\xfa\xaf\x00\x00\x1e\x03<対象サーボ数(1B)><サーボID_1(1B)><角度_1(2B-S16)>...<サーボID_N><角度_N(2B-S16)><CHECKSUM>
```
