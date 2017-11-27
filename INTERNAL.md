# Edison版Sota君の制御方法

## LED制御

I2C Bus=1 Chip-Addr=5の以下のアドレスにRGB値を書き込むことで光らせる

* 右目: 0x02(R), 0x03(G), 0x04(B)
* 左目: 0x05(R), 0x06(G), 0x07(B)

```
$ i2cset 1 5 0x02 0xff  # 右目を赤くする (0xFF0000)
$ i2cset 1 5 0x03 0xff  # 右目を黄色にする(0xFFFF00)
$ i2cset 1 5 0x02 0x00  # 右目を緑色にする (0x00FF00)
```

## サーボ制御

/dev/ttyMFD1 を使って制御。エコーありなので適宜readをかける。

checksumは3バイト以降の排他的論理和を計算。

まだ分析途中。

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

スペースより後ろは恐らく何でも良いと思われるが、
straceで得られた結果をそのまま利用。

```
\xfa\xaf\x00\x00\x23\x03\x08\x01\x00\x00\x02\x00\x00\x03\x00\x00\x04\x00\x00\x05\x00\x00\x06\x00\x00\x07\x00\x00\x08\x00\x00\x20
\xfa\xaf\x00\x00\x1e\x03\x08\x01\x00\x00\x02\xe5\xfc\x03\x00\x00\x04\x1b\x03\x05\x00\x00\x06\x00\x00\x07\x00\x00\x08\x00\x00\x1c
```

### サーボON + サーボ位置指定

チェックサムは二回目の\xfa\xaf以降のメッセージに対するものなので、35バイト以降を利用して求める。
A1-A8は対応するサーボの数値で16bit SignedInt LEで指定する。

```
\xfa\xaf\x00\x00\x23\x03\x08\x01\x64\x01\x02\x64\x01\x03\x64\x01\x04\x64\x01\x05\x64\x01\x06\x64\x01\x07\x64\x01\x08\x64\x01\x20
\xfa\xaf\x00\x00\x1e\x03\x08\x01<A1>\x02<A2>\x03<A3>\x04<A4>\x05<A5>\x06<A6>\x07<A7>\x08<A8><CHECKSUM>
```
