import requests
import logging

class NotificationManager:
    def __init__(self, config):
        self.enabled = config['simplepush_enabled']
        self.key = config['simplepush_key']
        self.url = config['simplepush_url']
        self.logger = logging.getLogger(__name__)

    def send_notification(self, title, message, event="airbnb-access"):
        if not self.enabled:
            self.logger.debug("Simplepush is not enabled. Skipping notification.")
            return
        url = f"{self.url}/{self.key}/{title}/{message}/event/{event}"
        response = requests.get(url)
        if response.status_code != 200:
            self.logger.error("Failed to send Simplepush notification")
        else:
            self.logger.debug("Simplepush notification sent successfully")
