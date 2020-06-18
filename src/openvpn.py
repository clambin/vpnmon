import re
import requests
import logging
from pimetrics.probe import FileProbe, APIProbe
from prometheus_client import Gauge

GAUGES = {
    'client_auth_read':
        Gauge('openvpn_client_auth_read_bytes_total', 'Total amount of authentication traffic read, in bytes.'),
    'client_pre_compress':
        Gauge('openvpn_client_pre_compress_bytes_total', 'Total amount of data before compression, in bytes.'),
    'client_pre_decompress':
        Gauge('openvpn_client_pre_decompress_bytes_total', 'Total amount of data before decompression, in bytes.'),
    'client_post_compress':
        Gauge('openvpn_client_post_compress_bytes_total', 'Total amount of data after compression, in bytes.'),
    'client_post_decompress':
        Gauge('openvpn_client_post_decompress_bytes_total', 'Total amount of data after decompression, in bytes.'),
    'client_tcp_udp_read':
        Gauge('openvpn_client_tcp_udp_read_bytes_total', 'Total amount of TCP/UDP traffic read, in bytes.'),
    'client_tcp_udp_write':
        Gauge('openvpn_client_tcp_udp_write_bytes_total', 'Total amount of TCP/UDP traffic written, in bytes.'),
    'client_tun_tap_read':
        Gauge('openvpn_client_tun_tap_read_bytes_total', 'Total amount of TUN/TAP traffic read, in bytes.'),
    'client_tun_tap_write':
        Gauge('openvpn_client_tun_tap_write_bytes_total', 'Total amount of TUN/TAP traffic written, in bytes.'),
    'client_status':
        Gauge('openvpn_client_status', 'Status of OpenVPN connection')
}


class OpenVPNProbe(FileProbe):
    metrics = {
        'client_auth_read':       r'Auth read bytes,(\d+)',
        'client_pre_compress':    r'pre-compress bytes,(\d+)',
        'client_pre_decompress':  r'pre-decompress bytes,(\d+)',
        'client_post_compress':   r'post-compress bytes,(\d+)',
        'client_post_decompress': r'post-decompress bytes,(\d+)',
        'client_tcp_udp_read':    r'TCP/UDP read bytes,(\d+)',
        'client_tcp_udp_write':   r'TCP/UDP write bytes,(\d+)',
        'client_tun_tap_read':    r'TUN/TAP read bytes,(\d+)',
        'client_tun_tap_write':   r'TUN/TAP write bytes,(\d+)',
    }

    def __init__(self, filename):
        FileProbe.__init__(self, filename)

    def report(self, output):
        for name, value in output.items():
            GAUGES[name].set(value)

    def process(self, content):
        output = {}
        for name, regex in self.metrics.items():
            result = re.search(regex, content)
            if result:
                value = int(result.group(1))
                output[name] = value
        return output


class OpenVPNStatusProbe(APIProbe):
    def __init__(self, token=None, proxies=None):
        self.token = token
        proxy_dict = None
        if proxies:
            proxy_dict = {proxy.split(':')[0]: proxy for proxy in proxies.split(',')}
        super().__init__('https://ipinfo.io', proxies=proxy_dict)

    def report(self, output):
        GAUGES['client_status'].set(1 if output is True else 0)

    def measure(self):
        try:
            response = self.get(params={'token': self.token} if self.token else None)
            logging.debug(f'response: {response.status_code} - {response.json()}')
            if response.status_code == 200:
                return True
            else:
                logging.warning(f'OpenVPNStatusProbe failed: {response.status_code}')
        except requests.exceptions.RequestException as e:
            logging.warning(f'OpenVPNStatusProbe failed: {e}')
        return False
