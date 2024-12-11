import argparse
import logging
import urllib3
import datetime
from config import load_config
from unifi_access import UnifiAccessManager
from hostex_api import HostexManager
from ics_parser import ICSParser
from notification import NotificationManager
from utils import setup_logging

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_across_systems(hostex_reservations, ics_reservations, unifi_visitors):
    discrepancies = []
    today = datetime.date.today()
    next_month = today + datetime.timedelta(days=30)
    
    # Filter relevant Hostex reservations
    relevant_hostex = [
        r for r in hostex_reservations 
        if today <= datetime.datetime.strptime(r["check_in_date"], "%Y-%m-%d").date() <= next_month 
        and r["status"] == "accepted"
    ]
    
    # Create lookup dictionaries by date range
    hostex_lookup = {
        (r["check_in_date"], r["check_out_date"]): r 
        for r in relevant_hostex
    }
    
    ics_lookup = {
        (r["check_in_date"].strftime("%Y-%m-%d"), r["check_out_date"].strftime("%Y-%m-%d")): r 
        for r in ics_reservations
    }
    
    # Check Hostex entries against ICS
    for dates, hostex_res in hostex_lookup.items():
        if dates not in ics_lookup:
            discrepancies.append(
                f"Hostex reservation for {hostex_res['guests'][0]['name']} "
                f"({dates[0]} to {dates[1]}) not found in ICS calendar"
            )
        else:
            # Verify phone number last 4 digits match
            hostex_phone = hostex_res['guests'][0].get('phone', '')[-4:]
            ics_phone = ics_lookup[dates]['guests'][0].get('phone', '')[-4:]
            if hostex_phone and ics_phone and hostex_phone != ics_phone:
                discrepancies.append(
                    f"Phone number mismatch for {hostex_res['guests'][0]['name']}: "
                    f"Hostex: {hostex_phone}, ICS: {ics_phone}"
                )
    
    return discrepancies

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
            hostex_reservations = hostex_manager.fetch_reservations()
        else:
            hostex_reservations = []
            
        if config['use_ics']:
            logger.info("Parsing ICS file")
            ics_reservations = ics_parser.parse_ics()
        else:
            ics_reservations = []
            
        # Filter and log relevant reservations
        today = datetime.date.today()
        next_month = today + datetime.timedelta(days=30)
        relevant_reservations = [
            r for r in hostex_reservations 
            if today <= datetime.datetime.strptime(r["check_in_date"], "%Y-%m-%d").date() <= next_month 
            and r["status"] == "accepted"
        ]
        
        logger.info(f"Found {len(relevant_reservations)} entries in Hostex API within the next 30 days")
        
        for res in relevant_reservations:
            guest_name = res["guests"][0]["name"] if res["guests"] else "Guest"
            phone_number = res["guests"][0].get("phone", "") if res["guests"] else ""
            logger.debug(
                f"Hostex Guest: {guest_name}, "
                f"Stay: {res['check_in_date']} to {res['check_out_date']}, "
                f"Phone: {phone_number}"
            )
            
        # Verify consistency across systems
        discrepancies = verify_across_systems(
            hostex_reservations, 
            ics_reservations,
            unifi_manager.fetch_visitors()
        )
        
        # Process reservations
        logger.info(f"Processing {len(relevant_reservations)} reservations")
        unifi_manager.process_reservations(relevant_reservations)
        
        logger.info("Checking and updating PINs for existing visitors")
        unifi_manager.check_and_update_pins()
        
        summary = unifi_manager.generate_summary()
        if discrepancies:
            summary += "\n\nDiscrepancies Found:\n" + "\n".join(discrepancies)
            
        logger.info(summary)

        total_visitors = len(unifi_manager.fetch_visitors())
        logger.info(f"Total UniFi Access visitors remaining after cleanup: {total_visitors}")

        if config['simplepush_enabled'] and (unifi_manager.has_changes() or discrepancies):
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
