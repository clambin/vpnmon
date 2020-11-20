import logging
from prometheus_client import start_http_server
from vpnmon.version import version
from vpnmon.configuration import print_configuration
from vpnmon.openvpn import OpenVPNProbe, OpenVPNStatusProbe
from pimetrics.scheduler import Scheduler


def initialise(config):
    scheduler = Scheduler()

    try:
        scheduler.register(OpenVPNProbe(config.client_status), 5)
    except FileNotFoundError as err:
        logging.warning(f'Could not add OpenVPN monitor: {err}')

    if config.monitor_status:
        scheduler.register(OpenVPNStatusProbe(config.token, config.proxy), 300)

    return scheduler


def vpnmon(config):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if config.debug else logging.INFO)
    logging.info(f'Starting vpnmon v{version}')
    logging.info(f'Configuration: {print_configuration(config)}')

    start_http_server(config.port)

    scheduler = initialise(config)
    if config.once:
        scheduler.run(once=True)
    else:
        while True:
            scheduler.run(duration=config.interval)
    return 0
