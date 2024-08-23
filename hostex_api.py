import requests
import logging

class HostexManager:
    def __init__(self, config):
        self.api_url = config['hostex_api_url']
        self.api_key = config['hostex_api_key']
        self.logger = logging.getLogger(__name__)

    def fetch_reservations(self):
        url = f"{self.api_url}/reservations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            reservations = response.json()["data"]["reservations"]
            self.logger.debug(f"Fetched {len(reservations)} reservations from Hostex")
            return reservations
        else:
            self.logger.error(f"Failed to fetch reservations from Hostex. Status code: {response.status_code}")
            return []
