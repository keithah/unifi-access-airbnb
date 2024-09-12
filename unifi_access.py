import requests
import datetime
import json
import logging

class UnifiAccessManager:
    def __init__(self, config):
        self.api_host = config['api_host']
        self.api_token = config['api_token']
        self.default_door_group_id = config.get('default_door_group_id', '')
        self.check_in_time = datetime.time.fromisoformat(config['check_in_time'])
        self.check_out_time = datetime.time.fromisoformat(config['check_out_time'])
        self.pin_code_digits = config['pin_code_digits']
        self.logger = logging.getLogger(__name__)
        self.changes = {'added': [], 'deleted': [], 'unchanged': []}
        
        self.logger.debug(f"Loaded default_door_group_id from config: {self.default_door_group_id}")
        if not self.default_door_group_id:
            self.logger.warning("default_door_group_id is not set in config. Attempting to fetch available door groups.")
            self.set_default_door_group()
        else:
            self.logger.debug(f"Initialized with default_door_group_id: {self.default_door_group_id}")

    def set_default_door_group(self):
        door_groups = self.fetch_door_groups()
        if len(door_groups) == 1:
            self.default_door_group_id = door_groups[0]['id']
            self.logger.info(f"Automatically set default_door_group_id to the only available group: {self.default_door_group_id}")
        elif len(door_groups) > 1:
            self.logger.error("Multiple door groups available. Please specify default_group_id in unifi.conf")
            raise ValueError("Multiple door groups available. Please specify default_group_id in unifi.conf")
        else:
            self.logger.error("No door groups available")
            raise ValueError("No door groups available")

    def create_visitor(self, first_name, last_name, start_time, end_time):
        url = f"{self.api_host}/api/v1/developer/visitors"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "start_time": start_time,
            "end_time": end_time,
            "visit_reason": "Other",
            "resources": [
                {
                    "id": self.default_door_group_id,
                    "type": "door_group"
                }
            ]
        }
        
        self.logger.debug(f"Creating visitor with data: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(url, json=data, headers=headers, verify=False)
            self.logger.debug(f"API response status code: {response.status_code}")
            self.logger.debug(f"API response content: {response.text}")
            
            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_data = response.json()
            if response_data.get('code') == 'SUCCESS':
                visitor_id = response_data.get('data', {}).get('id')
                if visitor_id:
                    self.logger.debug(f"Created visitor with ID: {visitor_id}")
                    return True
                else:
                    self.logger.error("Visitor ID not found in the response")
                    return False
            else:
                self.logger.error(f"API returned an error: {response_data.get('msg')}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return False

    def fetch_visitors(self):
        url = f"{self.api_host}/api/v1/developer/visitors"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        self.logger.debug(f"Fetch visitors API response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                self.logger.error(f"Unexpected response format: {data}")
                return []
        else:
            self.logger.error("Failed to fetch existing visitors")
            return []

    def delete_visitor(self, visitor_id, is_completed=False):
        url = f"{self.api_host}/api/v1/developer/visitors/{visitor_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        params = {"is_force": "true"} if is_completed else {}
        
        response = requests.delete(url, headers=headers, params=params, verify=False)
        self.logger.debug(f"Delete visitor API response status code: {response.status_code}")
        
        if response.status_code != 200:
            self.logger.error(f"Failed to delete visitor account: {visitor_id}")
            return False
        return True

    def process_reservations(self, reservations):
        today = datetime.date.today()
        next_month = today + datetime.timedelta(days=30)
        existing_visitors = self.fetch_visitors()

        self.logger.debug(f"Processing {len(reservations)} reservations")

        for reservation in reservations:
            check_in_date = datetime.datetime.strptime(reservation["check_in_date"], "%Y-%m-%d").date()
            check_out_date = datetime.datetime.strptime(reservation["check_out_date"], "%Y-%m-%d").date()

            if today <= check_in_date <= next_month and reservation["status"] == "accepted":
                guest_name = reservation["guests"][0]["name"] if reservation["guests"] else "Guest"
                first_name, last_name = guest_name.split(" ", 1) if " " in guest_name else (guest_name, "")

                existing_visitor = next(
                    (v for v in existing_visitors if
                     datetime.datetime.fromtimestamp(int(v["start_time"])).date() == check_in_date and
                     datetime.datetime.fromtimestamp(int(v["end_time"])).date() == check_out_date),
                    None
                )

                if existing_visitor:
                    self.changes['unchanged'].append(f"{existing_visitor['first_name']} {existing_visitor['last_name']}")
                else:
                    start_datetime = datetime.datetime.combine(check_in_date, self.check_in_time)
                    end_datetime = datetime.datetime.combine(check_out_date, self.check_out_time)
                    start_timestamp = int(start_datetime.timestamp())
                    end_timestamp = int(end_datetime.timestamp())
                    
                    success = self.create_visitor(first_name, last_name, start_timestamp, end_timestamp)
                    if success:
                        self.changes['added'].append(guest_name)
                    else:
                        self.logger.error(f"Failed to create visitor: {guest_name}")

        for visitor in existing_visitors:
            visitor_end = datetime.datetime.fromtimestamp(int(visitor["end_time"])).date()
            is_completed = visitor.get("status") == "VISITED"
            if visitor_end < today or is_completed:
                success = self.delete_visitor(visitor["id"], is_completed)
                if success:
                    self.changes['deleted'].append(f"{visitor['first_name']} {visitor['last_name']}")
                else:
                    self.logger.error(f"Failed to delete visitor: {visitor['first_name']} {visitor['last_name']}")

    def generate_summary(self):
        summary = "Hostex-UniFi Access Summary:\n"
        unchanged_names = ", ".join(self.changes['unchanged'])
        summary += f"{len(self.changes['unchanged'])} existing visitors unchanged ({unchanged_names})\n"
        if self.changes['deleted']:
            deleted_names = ", ".join(self.changes['deleted'])
            summary += f"{len(self.changes['deleted'])} visitor(s) deleted ({deleted_names})\n"
        if self.changes['added']:
            added_names = ", ".join(self.changes['added'])
            summary += f"{len(self.changes['added'])} visitor(s) added ({added_names})\n"
        return summary.strip()

    def has_changes(self):
        return bool(self.changes['added'] or self.changes['deleted'])

    def fetch_door_groups(self):
        url = f"{self.api_host}/api/v1/developer/door_groups"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        self.logger.debug(f"Fetch door groups API response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                self.logger.error(f"Unexpected response format: {data}")
                return []
        else:
            self.logger.error("Failed to fetch door groups")
            return []

    def print_door_groups(self):
        door_groups = self.fetch_door_groups()
        if door_groups:
            print("Available Door Groups:")
            for group in door_groups:
                print(f"ID: {group['id']}, Name: {group['name']}")
        else:
            print("No door groups found or failed to fetch door groups.")
