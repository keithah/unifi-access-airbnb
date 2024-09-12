# UniFi Access Airbnb Integration

This project integrates UniFi Access with Airbnb reservations, automating the process of creating and managing visitor access for your Airbnb guests.

## Features

- Fetch reservations from Hostex API or Airbnb ICS feed
- Create UniFi Access visitor accounts for upcoming guests
- Assign PIN codes to visitors based on their phone number
- Automatically delete past or completed visitor accounts
- Send notifications via Simplepush for updates and failures

## Prerequisites

- Python 3.7+
- UniFi Access system
- Airbnb account with ICS feed URL or Hostex API access

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/unifi-access-airbnb.git
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
- `-l [LOG_FILE]` or `--log [LOG_FILE]`: Specify a log file
- `--list-door-groups`: List available door groups

## Configuration

Edit the `unifi.conf` file with your specific settings. Key sections include:
- `[UniFi]`: UniFi Access API settings
- `[Hostex]`: Hostex API settings (if used)
- `[Airbnb]`: Airbnb ICS feed URL (if used)
- `[Door]`: Default door group ID for visitor access
- `[Visitor]`: Check-in and check-out times

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


