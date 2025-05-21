import requests
from app.config.config import config
from app.services.ip_update.cloudflare import Cloudflare
from app.utils.log import output_log
from app.utils.rabbitmq_publisher import RabbitMQPublisher

times = -1

def _access_check():
    try:
        response = requests.get("https://traefik.tenawalcott.com", timeout=5)
        output_log(response.status_code, "debug")
        return response.status_code
    except requests.exceptions.RequestException as e:
        return 500

def _ip_check():
    response = requests.get("https://api.ipify.org?format=json", timeout=5)
    return response.json()["ip"]

def ip_test_main():
    global times
    if _access_check() != 200:
        output_log(f"Access Check Failed with code {_access_check()}", "error")
        zone_ids = config.cloudflare_zone_id
        new_ip = _ip_check()
        cf = Cloudflare(zone_ids[0], config.cloudflare_api_token[0])
        current_ip = cf.get_dns_record("traefik.tenawalcott.com")["content"]
        if current_ip == new_ip:
            output_log(f"Treafik is not Accessble", "info")
            return
        output_log(f"Current IP: {current_ip}; New IP: {new_ip}; Zone IDs: {zone_ids}", "info")
        r = RabbitMQPublisher()
        r.publish(f"Homelab IP has Changed. Current IP: {current_ip}; New IP: {new_ip}")
        for i in range(len(zone_ids)):
            cf = Cloudflare(config.cloudflare_zone_id[i], config.cloudflare_api_token[i])
            cf.update_dns(current_ip, new_ip)
    else:
        output_log("Access Check Successful", "info")
        times += 1
        if times == 0:
            r = RabbitMQPublisher()
            cf = Cloudflare(config.cloudflare_zone_id[0], config.cloudflare_api_token[0])
            current_ip = cf.get_dns_record("traefik.tenawalcott.com")["content"]
            output_log(f"Current IP: {current_ip}", "info")
            r.publish(f"IP Check is Running. Current IP: {current_ip}")

def ip_test_schedule_report():
    global times
    r = RabbitMQPublisher()
    r.publish(f"Access Check is running with {times} checks during the past 24 hours")
    times = 0
