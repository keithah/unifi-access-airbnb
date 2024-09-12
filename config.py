import configparser
import logging

logger = logging.getLogger(__name__)

def load_config():
    config = configparser.ConfigParser()
    config.read('unifi.conf')
    
    logger.debug("Loaded sections from unifi.conf: %s", config.sections())
    
    if 'Door' not in config:
        logger.error("'Door' section not found in unifi.conf")
    elif 'default_group_id' not in config['Door']:
        logger.error("'default_group_id' not found in 'Door' section of unifi.conf")
    else:
        logger.debug("Found default_group_id in config: %s", config['Door']['default_group_id'])

    return {
        'api_host': config['UniFi']['api_host'],
        'api_token': config['UniFi']['api_token'],
        'hostex_api_url': config['Hostex']['api_url'],
        'hostex_api_key': config['Hostex']['api_key'],
        'ics_url': config.get('Airbnb', 'ics_url', fallback=None),
        'simplepush_enabled': config['Simplepush'].getboolean('enabled', fallback=False),
        'simplepush_key': config['Simplepush'].get('key', fallback=None),
        'simplepush_url': config['Simplepush'].get('url', fallback=None),
        'default_door_group_id': config['Door'].get('default_group_id', ''),
        'check_in_time': config['Visitor']['check_in_time'],
        'check_out_time': config['Visitor']['check_out_time'],
        'use_hostex': 'Hostex' in config and config['Hostex']['api_key'],
        'use_ics': config.get('Airbnb', 'ics_url', fallback=None) is not None,
        'log_file': config['General']['log_file'],
        'pin_code_digits': int(config['General']['pin_code_digits'])
    }

    logger.debug("Loaded configuration: %s", {k: v for k, v in config.items() if k != 'api_token'})
    return config
