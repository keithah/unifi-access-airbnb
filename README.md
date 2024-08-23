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

## Configuration

Edit the `unifi.conf` file with your specific settings. Here's an explanation of each section:

- `[UniFi]`: UniFi Access API settings
- `[Hostex]`: Hostex API settings (if used)
- `[Airbnb]`: Airbnb ICS feed URL (if used)
- `[Simplepush]`: Simplepush notification settings
- `[Door]`: Default door group ID for visitor access
- `[Visitor]`: Check-in and check-out times
- `[General]`: General settings like log file name and PIN code length

## Usage

Run the script using:
python main.py

Optional arguments:
- `-v` or `--verbose`: Increase output verbosity
- `-l [LOG_FILE]` or `--log [LOG_FILE]`: Specify a log file (default is set in the config file)

## Scheduling

To run the script automatically, you can set up a cron job. For example, to run it every hour:

1. Open your crontab file:
crontab -e
2. Add the following line (adjust the path as needed):
0 * * * * /usr/bin/python3 /path/to/unifi-access-airbnb/main.py

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- UniFi Access for their API
- Hostex for their reservation management API
- Airbnb for providing ICS feed functionality
- Simplepush for their notification service

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.

