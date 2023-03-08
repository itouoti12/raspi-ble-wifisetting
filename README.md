# raspiのwifi設定をbluetoothから行う

![gif](assets/raspi_ble.gif)

# インストール
- ラズパイに
- `sudo pip3 install pybleno`

# 起動
- `sudo python3 main.py`

# デバッグ
- iosアプリのLightBlueを使うとやりやすい

# uuid
https://uuid.doratool.com/
ここで生成

# ssid
ssid取得には subprocessライブラリを使えば取れる

# ラズパイ cliベースでwifi設定をする

- sudo bash -c 'wpa_passphrase "wifi SSID名" "パスワード" >> /etc/wpa_supplicant/wpa_supplicant.conf'
- sudo vi /etc/wpa_supplicant/wpa_supplicant.conf で追記前から記述のあったnetworkの記載を削除する（追記された方を残す）

- wpa_cli -i wlan0 reconfigure
切り替わらない場合
- sudo reboot

# ラズパイ　自動起動設定 python
- サービスの設定ファイルを作る

cd /usr/lib/systemd/system
- 設定ファイル作成
sudo vi  ble_wifi.service

- 記述内容
起動ファイルが
`/home/pi/github/raspi-ble-wifisetting/systemctl_main.py`にある想定

```
[Unit]
Description=Wifi Setting from ble

[Service]
ExecStart=python3 systemctl_main.py
WorkingDirectory=/home/pi/github/raspi-ble-wifisetting
Type=simple
Restart=on-failure
RestartSec=15
KillMode=process

[Install]
WantedBy=multi-user.target
```

- デーモンの再読み込み

    `sudo systemctl daemon-reload`

- サービスの実行

    `sudo systemctl start ble_wifi` 

- サービスの起動確認

    `sudo systemctl status ble_wifi` 

- サービスの自動起動を有効

    `sudo systemctl enable ble_wifi`

- サービスの自動起動状態を確認

    `systemctl is-enabled ble_wifi` 

- サービスの停止

    `sudo systemctl stop ble_wifi` 

- サービスの自動起動を無効

    `sudo systemctl disable ble_wifi`
