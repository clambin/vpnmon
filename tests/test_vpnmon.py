import argparse
from src.vpnmon import vpnmon, initialise
from src.openvpn import OpenVPNProbe, OpenVPNStatusProbe


def test_initialise():
    config = argparse.Namespace(interval=0, port=8080,
                                client_status='client.status',
                                monitor_status=True, token='123', proxies='http://localhost:8888',
                                once=True, stub=True, debug=True)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 2
    assert type(scheduler.scheduled_items[0].probe) is OpenVPNProbe
    assert type(scheduler.scheduled_items[1].probe) is OpenVPNStatusProbe


def test_bad_vpn_file():
    config = argparse.Namespace(interval=0, port=8080,
                                client_status='notafile', monitor_status=False,
                                once=True, stub=True, debug=True)
    scheduler = initialise(config)
    assert len(scheduler.scheduled_items) == 0


def test_vpnmon():
    config = argparse.Namespace(interval=0, port=8080,
                                client_status='client.status', monitor_status=False,
                                once=True, stub=True, debug=True)
    assert vpnmon(config) == 0
