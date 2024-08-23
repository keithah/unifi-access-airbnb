import argparse
import logging
from config import load_config
from unifi_access import UnifiAccessManager
from hostex_api import HostexManager
from ics_parser import ICSParser
from notification import NotificationManager
from utils import setup_logging

def main():
    parser = argparse.ArgumentParser(description="UniFi Access Visitor Management")
    parser.add_argument('-v', '--verbose', action='store_true', help="Increase output verbosity")
    parser.add_argument('-l', '--log', help="Log output to file")
    args = parser.parse_args()

    config = load_config()
    log_file = args.log or config['log_file']
    logger = setup_logging(args.verbose, log_file)

    unifi_manager = UnifiAccessManager(config)
    hostex_manager = HostexManager(config)
    ics_parser = ICSParser(config)
    notification_manager = NotificationManager(config)

    try:
        logger.debug("Script started")
        
        if config['use_hostex']:
            reservations = hostex_manager.fetch_reservations()
        elif config['use_ics']:
            reservations = ics_parser.parse_ics()
        else:
            logger.error("No valid reservation source configured")
            return

        unifi_manager.process_reservations(reservations)
        
        summary = unifi_manager.generate_summary()
        logger.info(summary)

        if config['simplepush_enabled'] and unifi_manager.has_changes():
            notification_manager.send_notification("UniFi Access Update", summary)

        logger.debug("Script completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logger.debug("Script execution finished")

if __name__ == "__main__":
    main()
