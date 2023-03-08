from pybleno import Characteristic, Descriptor
import subprocess

WRITE_WIFI_SSID_UUID = 'd6f2e846-8212-085e-c65f-343fd0b411e7'
WRITE_WIFI_PASSWORD_UUID = 'd6f2e846-8212-085e-c65f-343fd0b411e8'
WRITE_WIFI_SETUP_UUID = 'd6f2e846-8212-085e-c65f-343fd0b411e9'

g_ssid = ''
g_password = ''

class WifiWriteSSIDCharacterristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': WRITE_WIFI_SSID_UUID,
            'properties': ['write', 'read'],
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': 'SSIDを書き込む'.encode()
                })
            ],
            'value': None
        })

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        """
        WifiのSSIDを設定する
        """
        global g_ssid

        # dataの中にはbytearrayで送られてくる
        ssid = data.decode()
        print('WifiWriteSSIDCharacterristic - %s - onWriteRequest: value = %s' %
              (self['uuid'], ssid))
        g_ssid = ssid
        callback(Characteristic.RESULT_SUCCESS)

    def onReadRequest(self, offset, callback):
        global g_ssid

        print('WifiWriteSSIDCharacterristic - %s - onReadRequest: value = %s' %
              (self['uuid'], g_ssid))
        callback(Characteristic.RESULT_SUCCESS, g_ssid.encode('utf-8'))


class WifiWritePASSWORDCharacterristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': WRITE_WIFI_PASSWORD_UUID,
            'properties': ['write', 'read'],
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': 'passwordを書き込む'.encode()
                })
            ],
            'value': None
        })

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        """
        WifiのPASSWORDを設定する
        """

        global g_password

        # dataの中にはbytearrayで送られてくる
        password = data.decode()
        print('WifiWritePASSWORDCharacterristic - %s - onWriteRequest: value = %s' %
              (self['uuid'], password))
        g_password = password
        callback(Characteristic.RESULT_SUCCESS)

    def onReadRequest(self, offset, callback):
        global g_password

        print('WifiWritePASSWORDCharacterristic - %s - onReadRequest: value = %s' %
              (self['uuid'], g_password))
        callback(Characteristic.RESULT_SUCCESS, g_password.encode('utf-8'))


class WifiSetupCharacterristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': WRITE_WIFI_SETUP_UUID,
            'properties': ['write'],
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': 'wifiの設定を更新'.encode()
                })
            ],
            'value': None
        })

    def updateWpaSupplicant(self, ssid, password):

        # Read file WPA supplicant
        networks = []
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as f:
            in_lines = f.readlines()

        # Discover networks
        out_lines = []
        networks = []
        i = 0
        isInside = False
        for line in in_lines:
            if "network={" == line.strip().replace(" ", ""):
                networks.append({})
                isInside = True
            elif "}" == line.strip().replace(" ", ""):
                i += 1
                isInside = False
            elif isInside:
                key_value = line.strip().split("=")
                networks[i][key_value[0]] = key_value[1]
            else:
                out_lines.append(line)

        print(networks)

        # Update network
        isFound = False
        for network in networks:
            if network["ssid"] == f"\"{ssid}\"":
                network["psk"] = f"{password}"
                isFound = True
                break

        if not isFound:
            networks = [{
                'ssid': f"\"{ssid}\"",
                'psk': f"{password}",
            }]

        # Generate new WPA Supplicant
        for network in networks:
            out_lines.append("network={\n")
            for key, value in network.items():
                out_lines.append(f"    {key}={value}\n")
            out_lines.append("}\n\n")

        # Write to WPA Supplicant
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
            for line in out_lines:
                f.write(line)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        """
        セットしたSSID,PASSWORDをもとにwifiの設定を変更する
        """
        global g_ssid
        global g_password

        if not g_ssid or not g_password:
            print(
                'WifiSetupCharacterristic - %s - onWriteRequest: setting is not complete' % (self['uuid']))
            callback(Characteristic.RESULT_UNLIKELY_ERROR)

        else:
            print(
                'WifiSetupCharacterristic - %s - onWriteRequest: start setup' % (self['uuid']))

            GET_SSID_PASS = f'wpa_passphrase {g_ssid} {g_password}'
            proc = subprocess.run(GET_SSID_PASS, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).stdout.decode().rstrip()
            print(proc)
            pass_idx = proc.rfind('psk=')
            pass_key = proc[pass_idx + 4: -1].strip().replace(" ", "")
            print(pass_key)

            # update wpa_supplicant file
            self.updateWpaSupplicant(g_ssid, pass_key)

            RECONFIGURE_WIFI = f'wpa_cli -i wlan0 reconfigure'
            proc = subprocess.run(RECONFIGURE_WIFI, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).stdout.decode().rstrip()
            if proc == "OK":
                print(
                    'WifiSetupCharacterristic - %s - onWriteRequest: finish setup' % (self['uuid']))
                callback(Characteristic.RESULT_SUCCESS)

            else:
                print(
                    'WifiSetupCharacterristic - %s - onWriteRequest: setup failed' % (self['uuid']))
                callback(Characteristic.RESULT_UNLIKELY_ERROR)
            
            g_ssid = ''
            g_password = ''
