from pybleno import Characteristic, Descriptor
import subprocess
import socket

READ_WIFI_UUID = '949de0a3-3120-bc67-8207-8ab7df630791'
READ_NETWORK_CONNECTION_UUID = '949de0a3-3120-bc67-8207-8ab7df630792'

class WifiReadCharacterristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': READ_WIFI_UUID,
            'properties': ['read'],
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': '設定中のwifi:SSID'.encode()
                })
            ],
            'value': None
        })

    def onReadRequest(self, offset, callback):
        """
        現在設定中のWifiのSSIDを取得する
        """

        GET_SSID_CMD = "iwconfig wlan0 |grep ESSID"
        proc = subprocess.run(GET_SSID_CMD, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.decode().rstrip()
        idx = proc.find('ESSID:')
        ssid = proc[idx + 7: -1]

        print('WifiReadCharacterristic - %s - onReadRequest: SSID = %s' %
              (self['uuid'], ssid))
        print(offset)

        callback(Characteristic.RESULT_SUCCESS, ssid.encode('utf-8'))

class ReadNetworkConnectionCharacterristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': READ_NETWORK_CONNECTION_UUID,
            'properties': ['read'],
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': 'ネットワーク接続確認'.encode()
                })
            ],
            'value': None
        })

    def onReadRequest(self, offset, callback):
        """
        ネットワークに接続できているかを確認する
        """

        isConnect = connected_internet_confirm()
        print('ReadNetworkConnectionCharacterristic - %s - onReadRequest: isConnect = %s' %
              (self['uuid'], isConnect))
        print(offset)

        res = 'no connection'
        if(isConnect):
            res = 'is connected'

        callback(Characteristic.RESULT_SUCCESS, res.encode('utf-8'))


def connected_internet_confirm(Host="8.8.8.8", port=53, timeout=3):
    """
        Host  "8.8.8.8" (google-public-dns-a.google.com).
        port  53/tcp.
        Service domain(DNS/TCP)
        timeout  3.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((Host,port))
        return True
    except socket.error as ex:
        print(ex)
        return False