import requests
import datetime
import json
import logging

class UnifiAccessManager:
    def __init__(self, config):
        self.api_host = config['api_host']
        self.api_token = config['api_token']
        self.default_door_group_id = config['default_door_group_id']
        self.check_in_time = datetime.time.fromisoformat(config['check_in_time'])
        self.check_out_time = datetime.time.fromisoformat(config['check_out_time'])
        self.pin_code_digits = config['pin_code_digits']
        self.logger = logging.getLogger(__name__)
        self.changes = {'added': [], 'deleted': [], 'unchanged': []}

    def create_visitor(self, first_name, last_name, remarks, phone_number, start_time, end_time):
        url = f"{self.api_host}/api/v1/developer/visitors"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        pin_code = phone_number[-self.pin_code_digits:] if phone_number and len(phone_number) >= self.pin_code_digits else ""
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "remarks": remarks,
            "mobile_phone": phone_number,
            "email": "",
            "visitor_company": "",
            "start_time": start_time,
            "end_time": end_time,
            "visit_reason": "Other",
            "resources": [
                {"id": self.default_door_group_id, "type": "door_group"}
            ]
        }
        response = requests.post(url, json=data, headers=headers, verify=False)
        if response.status_code != 200:
            self.logger.error(f"Failed to create visitor account for {first_name} {last_name}")
            return False
        else:
            visitor_id = response.json()["data"]["id"]
            return self.assign_pin_to_visitor(visitor_id, pin_code)

    def assign_pin_to_visitor(self, visitor_id, pin_code):
        url = f"{self.api_host}/api/v1/developer/visitors/{visitor_id}/pin_codes"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "pin_code": pin_code
        }
        response = requests.put(url, json=data, headers=headers, verify=False)
        if response.status_code != 200:
            self.logger.error(f"Failed to assign PIN code to visitor: {visitor_id}")
            return False
        else:
            return True

    def fetch_visitors(self):
        url = f"{self.api_host}/api/v1/developer/visitors"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()["data"]
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
        if response.status_code != 200:
            self.logger.error(f"Failed to delete visitor account: {visitor_id}")
            return False
        else:
            return True

    def process_reservations(self, reservations):
        today = datetime.date.today()
        next_month = today + datetime.timedelta(days=30)
        existing_visitors = self.fetch_visitors()

        for reservation in reservations:
            check_in_date = datetime.datetime.strptime(reservation["check_in_date"], "%Y-%m-%d").date()
            check_out_date = datetime.datetime.strptime(reservation["check_out_date"], "%Y-%m-%d").date()

            if today <= check_in_date <= next_month and reservation["status"] == "accepted":
                guest_name = reservation["guests"][0]["name"] if reservation["guests"] else "Guest"
                remarks = json.dumps(reservation)
                phone_number = reservation["guests"][0].get("phone", "") if reservation["guests"] else ""

                existing_visitor = next(
                    (v for v in existing_visitors if
                     datetime.datetime.fromtimestamp(v["start_time"]).date() == check_in_date and
                     datetime.datetime.fromtimestamp(v["end_time"]).date() == check_out_date),
                    None
                )

                if existing_visitor:
                    self.changes['unchanged'].append(f"{existing_visitor['first_name']} {existing_visitor['last_name']}")
                else:
                    start_datetime = datetime.datetime.combine(check_in_date, self.check_in_time)
                    end_datetime = datetime.datetime.combine(check_out_date, self.check_out_time)
                    start_timestamp = int(start_datetime.timestamp())
                    end_timestamp = int(end_datetime.timestamp())
                    
                    success = self.create_visitor(guest_name, "", remarks, phone_number, start_timestamp, end_timestamp)
                    if success:
                        self.changes['added'].append(guest_name)
                    else:
                        self.logger.error(f"Failed to create visitor: {guest_name}")

        for visitor in existing_visitors:
            visitor_end = datetime.datetime.fromtimestamp(visitor["end_time"]).date()
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
