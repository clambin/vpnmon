import pytest
import proxy
import time
from src.openvpn import OpenVPNProbe, OpenVPNStatusProbe


def test_vpn():
    probe = OpenVPNProbe('client.status')
    probe.run()
    measured = probe.measured()
    assert measured['client_tun_tap_read'] == 1
    assert measured['client_tun_tap_write'] == 2
    assert measured['client_tcp_udp_read'] == 3
    assert measured['client_tcp_udp_write'] == 4
    assert measured['client_auth_read'] == 5
    assert measured['client_pre_compress'] == 6
    assert measured['client_post_compress'] == 7
    assert measured['client_pre_decompress'] == 8
    assert measured['client_post_decompress'] == 9


def test_bad_file():
    with pytest.raises(FileNotFoundError):
        OpenVPNProbe('notafile')


def test_status():
    probe = OpenVPNStatusProbe()
    probe.run()
    assert probe.measured() is True


def test_status_without_proxy():
    probe = OpenVPNStatusProbe(proxies="https://localhost:8889")
    probe.run()
    assert probe.measured() is False


def test_status_with_proxy():
    with proxy.start(['--host', '127.0.0.1', '--port', '8888']):
        time.sleep(2)
        probe = OpenVPNStatusProbe(proxies="http://localhost:8888,https://localhost:8888")
        probe.run()
        assert probe.measured() is True


@pytest.mark.parametrize('proxies, result', [
    ('http://localhost:8888', {'http': 'http://localhost:8888'}),
    ('http://localhost:8888,https://localhost:8889',
     {'http': 'http://localhost:8888', 'https': 'http://localhost:8889'}),
    ('http://localhost:8888,https:/localhost:8889', {'http': 'http://localhost:8888'}),
    ('https:/localhost:8889', {}),
    ('', {}),
])
def test_proxy_parser(proxies, result):
    assert OpenVPNStatusProbe._parse_proxies(proxies) == result
