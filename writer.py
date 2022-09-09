import sys
import time
import json
from kafka import KafkaProducer


class KafkaWriter():
    def __init__(self, logger, params):
        try:
            self.logger = logger
            self.hosts = params["hosts"]
            self.topic = params["topic"]
            self.group_id = params["group_id"]
            self.retry_count = params["retry_count"]
            self.reconnect()
        except Exception as e:
            self.logger.exception("init error")

    def reconnect(self):
        self.producer = KafkaProducer(bootstrap_servers=self.hosts)
        self.logger.info('KafkaProducer reconnect success')

    def write_one_json(self, json_data):
        issend = False
        retry = self.retry_count
        while (retry > 0):
            try:
                output = json.dumps(json_data, ensure_ascii=False)
                output = output.encode("utf-8")
                self.producer.send(self.topic, value=output)
                self.producer.flush(timeout=3)
                issend = True
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("write error，start reconnect")
                self.reconnect()
        return issend

    def close(self):
        self.producer.close()


class FakeWriter(object):
    def __init__(self, logger, params):
        self.logger = logger

    def write_one_json(self, json_data):
        print(json_data)
        return True


    def cloes(self):
        pass

if __name__ == '__main__':
    # {"accept_time": 1554183932.893, "rule": "1566709\t0\t0\t1\twww.google.com\t0\t特朗普\t/search?\t!tbm\t!/complete/","platform": "ytb_p"}
    p = KafkaWriter()