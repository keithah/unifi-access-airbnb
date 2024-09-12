import argparse
import logging
import urllib3
from config import load_config
from unifi_access import UnifiAccessManager
from hostex_api import HostexManager
from ics_parser import ICSParser
from notification import NotificationManager
from utils import setup_logging

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="UniFi Access Visitor Management")
    parser.add_argument('-v', '--verbose', action='store_true', help="Increase output verbosity")
    parser.add_argument('-l', '--log', help="Log output to file")
    parser.add_argument('--list-door-groups', action='store_true', help="List available door groups")
    args = parser.parse_args()

    # Initialize logging first
    logger = logging.getLogger(__name__)
    log_file = args.log or 'unifi_access.log'  # Default log file if not specified
    logger = setup_logging(args.verbose, log_file)

    try:
        config = load_config()
        logger.debug(f"Loaded config: {config}")
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return

    try:
        unifi_manager = UnifiAccessManager(config)
    except ValueError as e:
        logger.error(f"Error initializing UnifiAccessManager: {str(e)}")
        return

    if args.list_door_groups:
        unifi_manager.print_door_groups()
        return

    hostex_manager = HostexManager(config)
    ics_parser = ICSParser(config)
    notification_manager = NotificationManager(config)

    try:
        logger.info("Script started")
        
        if config['use_hostex']:
            logger.info("Fetching reservations from Hostex")
            reservations = hostex_manager.fetch_reservations()
        elif config['use_ics']:
            logger.info("Parsing ICS file")
            reservations = ics_parser.parse_ics()
        else:
            logger.error("No valid reservation source configured")
            return

        logger.info(f"Processing {len(reservations)} reservations")
        unifi_manager.process_reservations(reservations)
        
        logger.info("Checking and updating PINs for existing visitors")
        unifi_manager.check_and_update_pins()
        
        summary = unifi_manager.generate_summary()
        logger.info(summary)

        total_visitors = len(unifi_manager.fetch_visitors())
        logger.info(f"Total visitors remaining after cleanup: {total_visitors}")

        if config['simplepush_enabled'] and unifi_manager.has_changes():
            notification_manager.send_notification("UniFi Access Update", summary)
            logger.info("Simplepush notification sent")
        else:
            logger.info("No Simplepush notification sent (no changes or Simplepush not enabled)")

        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logger.info("Script execution finished")

if __name__ == "__main__":
    main()
