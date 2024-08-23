import requests
import icalendar
import datetime
import logging

class ICSParser:
    def __init__(self, config):
        self.ics_url = config['ics_url']
        self.logger = logging.getLogger(__name__)

    def parse_ics(self):
        response = requests.get(self.ics_url)
        cal = icalendar.Calendar.from_ical(response.text)
        reservations = []
        for event in cal.walk("VEVENT"):
            start = event.get("DTSTART").dt
            end = event.get("DTEND").dt
            description = event.get("DESCRIPTION", "")
            if not description:
                self.logger.debug(f"Skipping event with start date {start.date()} due to missing description")
                continue
            pin_code = ""
            for line in description.split("\n"):
                if line.startswith("Phone Number (Last 4 Digits):"):
                    pin_code = line.split(": ")[1].strip()
                    break
            reservations.append({
                "check_in_date": start.date() if isinstance(start, datetime.datetime) else start,
                "check_out_date": end.date() if isinstance(end, datetime.datetime) else end,
                "guests": [{"name": "Airbnb Guest", "phone": pin_code}],
                "status": "accepted"
            })
        self.logger.debug(f"Parsed {len(reservations)} reservations from ICS file")
        return reservations
