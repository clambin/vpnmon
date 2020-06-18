from src.vpnmon import vpnmon
from src.configuration import get_configuration

if __name__ == '__main__':
    vpnmon(get_configuration())
