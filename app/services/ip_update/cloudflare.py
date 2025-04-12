import requests
from app.utils.log import output_log


class Cloudflare:
    def __init__(self, zone_id, api_token):
        self.zone_id = zone_id
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self.base_url = (
            f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        )

    def __get_dns_records(self):
        response = requests.get(self.base_url, headers=self.headers, timeout=5)
        output_log(response.json(), "debug")
        return response.json()["result"]

    def get_dns_record(self, record_name):
        records = self.__get_dns_records()
        for record in records:
            if record["type"] == "A" and record["name"] == record_name:
                return record
        return None

    def __update_dns_record(self, record_id, new_ip, record_name):
        update_url = f"{self.base_url}/{record_id}"
        data = {
            "type": "A",
            "name": record_name,
            "content": new_ip,
            "ttl": 1,
            "proxied": False,
        }
        output_log(update_url, "debug")
        output_log(data, "debug")
        requests.put(update_url, headers=self.headers, json=data, timeout=5)

    def update_dns(self, current_ip, new_ip):
        records = self.__get_dns_records()
        for record in records:
            output_log(record, "debug")
            if record["type"] == "A" and record["content"] == current_ip:
                self.__update_dns_record(record["id"], new_ip, record["name"])
