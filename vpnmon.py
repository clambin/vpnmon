from vpnmon.vpnmon import vpnmon
from vpnmon.configuration import get_configuration

if __name__ == '__main__':
    vpnmon(get_configuration())
