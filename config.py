import configparser

def load_config():
    config = configparser.ConfigParser()
    config.read('unifi.conf')
    
    return {
        'api_host': config['UniFi']['api_host'],
        'api_token': config['UniFi']['api_token'],
        'hostex_api_url': config['Hostex']['api_url'],
        'hostex_api_key': config['Hostex']['api_key'],
        'ics_url': config.get('Airbnb', 'ics_url', fallback=None),
        'simplepush_enabled': config['Simplepush'].getboolean('enabled', fallback=False),
        'simplepush_key': config['Simplepush'].get('key', fallback=None),
        'simplepush_url': config['Simplepush'].get('url', fallback=None),
        'default_door_group_id': config['Door']['default_group_id'],
        'check_in_time': config['Visitor']['check_in_time'],
        'check_out_time': config['Visitor']['check_out_time'],
        'use_hostex': 'Hostex' in config and config['Hostex']['api_key'],
        'use_ics': config.get('Airbnb', 'ics_url', fallback=None) is not None,
        'log_file': config['General']['log_file'],
        'pin_code_digits': int(config['General']['pin_code_digits'])
    }
