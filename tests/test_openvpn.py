import pytest
import proxy
import threading
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


def run_proxy():
    proxy.main(['--host', '127.0.0.1', '--port', '8888'])


def test_status_with_proxy():
    # for some reason we're dragging in proxy-py 1.1.1, which doesn't have proxy.start
    threading.Thread(target=run_proxy)
    with proxy.start(['--host', '127.0.0.1', '--port', '8888']):
        probe = OpenVPNStatusProbe(proxies="https://localhost:8888")
        probe.run()
        assert probe.measured() is True