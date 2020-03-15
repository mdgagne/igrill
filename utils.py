from builtins import range
from config import strip_config
from igrill import IGrillMiniPeripheral, IGrillV2Peripheral, IGrillV3Peripheral, DeviceThread
import logging
import cayenne.client

config_requirements = {
    'specs': {
        'required_entries': {'devices': list, 'cayenne': dict},
    },
    'children': {
        'devices': {
            'specs': {
                'required_entries': {'name': str, 'type': str, 'address': str, 'topic': str, 'interval': int},
                'list_type': dict
            }
        },
        'cayenne': {
            'specs': {
                'required_entries':{'username': str,
                                    'password': str,
                                    'client-id':str}
            }
        }
    }
}


def log_setup(log_level, logfile):
    """Setup application logging"""

    numeric_level = logging.getLevelName(log_level.upper())
    if not isinstance(numeric_level, int):
        raise TypeError("Invalid log level: {0}".format(log_level))

    if logfile is not '':
        logging.info("Logging redirected to: ".format(logfile))
        # Need to replace the current handler on the root logger:
        file_handler = logging.FileHandler(logfile, 'a')
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for handler in log.handlers:  # remove all old handlers
            log.removeHandler(handler)
        log.addHandler(file_handler)

    else:
        logging.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s: %(message)s')

    logging.getLogger().setLevel(numeric_level)
    logging.info("log_level set to: {0}".format(log_level))


def publish(temperatures, battery, client):
    for i in range(1, 5):
        if temperatures[i]:
            client.fahrenheitWrite(i, temperatures[i])

    client.virtualWrite(1, battery/100.0, cayenne.client.TYPE_BATTERY, cayenne.client.UNIT_VOLTS)


def get_devices(device_config):
    if device_config is None:
        logging.warn('No devices in config')
        return {}

    device_types = {'igrill_mini': IGrillMiniPeripheral,
                    'igrill_v2': IGrillV2Peripheral,
                    'igrill_v3': IGrillV3Peripheral}

    return [device_types[d['type']](**strip_config(d, ['address', 'name'])) for d in device_config]


def get_device_threads(device_config, cayenne_config, run_event):
    if device_config is None:
        logging.warn('No devices in config')
        return {}

    return [DeviceThread(ind, d['name'], d['address'], d['type'], cayenne_config, d['topic'], d['interval'], run_event) for ind, d in
            enumerate(device_config)]

