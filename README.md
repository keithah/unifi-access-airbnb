This project integrates UniFi Access with Airbnb reservations, automating the process of creating and managing visitor access for your Airbnb guests.

## Features
- Fetch reservations from Hostex API or Airbnb ICS feed
- Create UniFi Access visitor accounts for upcoming guests
- Assign PIN codes to visitors based on their phone number
- Automatically delete past or completed visitor accounts
- Send notifications via Simplepush for updates and failures
- Cross-verify reservations between Hostex and ICS calendar
- Monitor and report discrepancies in booking data
- Detailed logging of all visitor management operations

## Prerequisites
- Python 3.7+
- UniFi Access system
- Airbnb account with ICS feed URL or Hostex API access
- [Optional] Simplepush account for notifications

## Installation
1. Clone the repository:

git clone https://github.com/keithah/unifi-access-airbnb.git

cd unifi-access-airbnb

2. Install the required packages:


pip install -r requirements.txt

3. Copy the example configuration file and edit it with your settings:

cp unifi.conf.example unifi.conf

nano unifi.conf

## Usage
Run the script using:

python3 main.py

Optional arguments:
- `-v` or `--verbose`: Increase output verbosity
- `-l [LOG_FILE]` or `--log [LOG_FILE]`: Specify a log file (default: unifi_access.log)
- `--list-door-groups`: List available door groups

## Configuration
Edit the `unifi.conf` file with your specific settings. Key sections include:
- `[UniFi]`: UniFi Access API settings
 - api_host: UniFi Access controller URL
 - api_token: Authentication token
- `[Hostex]`: Hostex API settings (if used)
 - api_url: Hostex API endpoint
 - api_key: Authentication key
- `[Airbnb]`: Airbnb ICS feed URL (if used)
 - ics_url: Calendar feed URL
- `[Door]`: Door access settings
 - default_group_id: Default door group ID for visitor access
- `[Visitor]`: Visit timing settings
 - check_in_time: Default check-in time (e.g., "14:30")
 - check_out_time: Default check-out time (e.g., "11:30")
- `[General]`: General settings
 - log_file: Path to log file
 - pin_code_digits: Number of digits for PIN codes
- `[Simplepush]`: Notification settings
 - enabled: Enable/disable notifications
 - key: Simplepush key
 - url: Simplepush API URL

## Logging and Monitoring
The script provides detailed logging of all operations:
- Reservation processing from Hostex and ICS
- Visitor creation and deletion in UniFi Access
- PIN code assignments and updates
- Cross-system verification results
- Errors and warnings

Logs can be viewed in real-time using the `-v` flag or reviewed in the log file.

## System Verification
The script performs several verification checks:
- Matches Hostex reservations with ICS calendar entries
- Verifies phone numbers and PIN codes across systems
- Reports discrepancies in dates or guest information
- Monitors UniFi Access visitor status

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support
If you encounter any issues or have questions:
1. Check the logs using verbose mode
2. Review your configuration file
3. Open an issue on GitHub with relevant logs and details```
