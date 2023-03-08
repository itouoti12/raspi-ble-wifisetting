import signal
import time
from pybleno import Bleno, BlenoPrimaryService
import sys
from WifiReadCharacterristic import *
from WifiWriteCharacterristic import *

GATT_UUID = '07bff984-4c5c-c51a-9a16-11f24f4fcaba'
SERVICE_UUID = '3bd5040f-cf5b-e98a-60ef-e961a8e507e4'

# setting whole pybleno
def onStateChange(state):
    print('on -> stateChange: ' + state)

    if (state == 'poweredOn'):
        bleno.startAdvertising('raspi-ble-setting', [GATT_UUID])
    else:
        bleno.stopAdvertising()


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' +
          ('error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': SERVICE_UUID,
                'characteristics': [
                    switsimulator_wifi_connection,
                    switsimulator_wifi_read,
                    switsimulator_wifi_set_ssid,
                    switsimulator_wifi_set_password,
                    switsimulator_wifi_setup,
                ]
            }),
        ])

def termed(signum, frame):
    print("call SIGTERM")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, termed)
    
    try:
        print('bleno - 起動')

        # 初期処理
        bleno = Bleno()
        bleno.on('stateChange', onStateChange)
        bleno.on('advertisingStart', onAdvertisingStart)

        # characteristic設定
        switsimulator_wifi_connection = ReadNetworkConnectionCharacterristic()
        switsimulator_wifi_read = WifiReadCharacterristic()
        switsimulator_wifi_set_ssid = WifiWriteSSIDCharacterristic()
        switsimulator_wifi_set_password = WifiWritePASSWORDCharacterristic()
        switsimulator_wifi_setup = WifiSetupCharacterristic()

        # 開始
        bleno.start()

        while True:
            print('now executing...')
            time.sleep(3)
    finally:
        print("bleno - 終了")
        # 終了処理
        bleno.stopAdvertising()
        bleno.disconnect()
        
