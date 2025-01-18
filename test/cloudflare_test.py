import unittest
from app.cloudflare import Cloudflare
from app.config.config import config
from app.ip_test import main
from app.slack import Slack
from app.config.config import config

class TestCloudflare(unittest.TestCase):
    '''
    def test_get_dns_records(self):
        cf = Cloudflare("b0e9e219f05bf7db56fc7db929f1248b")
        result = cf.get_dns_records()
        for record in result:
            if record["type"] == "A" and record["name"] == "minio.tenawalcott.com":
                print(record)
                break
        self.assertEqual(record["type"], "A")
        self.assertEqual(record["name"], "minio.tenawalcott.com")
        self.assertEqual(record["content"], "174.92.31.95")
        self.assertEqual(record["ttl"], 1)
        self.assertEqual(record["proxied"], False)

    def test_config(self):
        zone_id = config.cloudflare_zone_id
        print(zone_id)
        self.assertEqual(zone_id[0], "b0e9e219f05bf7db56fc7db929f1248b")
    def test_ip_check(self):
        main()
    def test_slack_message(self):
        s = Slack()
        s.send_message("Test message")
    def test_main(self):
        main()
    def test_updater(self):
        zoneids = config.cloudflare_zone_id
        for zoneid in zoneids:
            cf = Cloudflare(zoneid)
            cf.update_dns("174.92.31.95", "3.4.5.6")
    def test_update_dns_record(self):
        cf = Cloudflare("1f44a4b9cc44497bfd04b09047a7395a")
        cf.update_dns_record("256398dd7932d31aab144836e62eb392", "1.1.1.1", 'test2.dingyipeng.com')
'''

if __name__ == '__main__':
    unittest.main()