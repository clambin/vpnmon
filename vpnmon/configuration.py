import argparse

from vpnmon.version import version


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'on'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'off'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_configuration(args=None):
    default_interval = 5
    default_port = 8080
    default_vpn_client_status = 'client.status'

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser.add_argument('--interval', type=int, default=default_interval,
                        help=f'Time between measurements (default: {default_interval} sec)')
    parser.add_argument('--port', type=int, default=default_port,
                        help=f'Prometheus listener port (default: {default_port})')
    parser.add_argument('--once', action='store_true',
                        help='Measure once and then terminate')
    parser.add_argument('--stub', action='store_true',
                        help='Use stubs (for debugging only')
    parser.add_argument('--debug', action='store_true',
                        help='Set logging level to debug')
    # OpenVPN monitoring
    parser.add_argument('--client-status', default=default_vpn_client_status,
                        help='OpenVPN client status file')
    parser.add_argument('--monitor-status', type=str2bool, nargs='?', default=False,
                        help='Enable/disable OpenVPN client status monitoring (default: off)')
    parser.add_argument('--token', default='',
                        help='Token for https://ipinfo.io')
    parser.add_argument('--proxy', default='',
                        help='URL of OpenVPN proxy to check VPN connectivity. '
                             'Requires running a proxy alongside the openvpn server (eg haugene/transmission-openvpn)')
    return parser.parse_args(args)


def print_configuration(config):
    return ', '.join([f'{key}={val}' for key, val in vars(config).items()])
