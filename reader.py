#!/bin/env python
# -*- coding:utf8 -*-

import sys
from kafka import KafkaConsumer
import time
import json


class KafkaReader(object):
    def __init__(self, logger, params):
        self.logger = logger
        self.max_read_count = params["max_read_count"]
        self.retry_count = params["retry_count"]
        self.hosts = params["hosts"]
        self.topic = params["topic"]
        self.group_id = params["group_id"]
        self.reconnect()

    def reconnect(self):
        self.consumer = KafkaConsumer(self.topic,
                                      group_id=self.group_id,
                                      bootstrap_servers=self.hosts,  # )
                                      consumer_timeout_ms=5 * 1000)

    def read_docs(self):
        docs = []
        retry = self.retry_count
        for i in range(self.max_read_count):
            while retry > 0:
                try:
                    try:
                        messege = self.consumer.next()
                    except StopIteration:
                        time.sleep(2)
                        return docs
                    docs.append(json.loads(messege.value))
                    break
                except BaseException:
                    self.logger.exception("read docs exception")
                    retry -= 1
                    self.reconnect()
        return docs

    def close(self):
        self.consumer.close()


class FakeReader(object):
    def __init__(self, logger, params):
        self.logger = logger
        self.max_read_count = params["max_read_count"]
        self.fake_data = {
            "headers": {"User-Agent": "Mozilla/5.0"},
            "method": "get",
            #"url": "https://pubmed.ncbi.nlm.nih.gov/?term={}&page={}".format("cancer", 1)
            "url": "https://pubmed.ncbi.nlm.nih.gov/2021454/"
        }

    def read_docs(self):
        docs = []
        for i in range(self.max_read_count):
            docs.append(self.fake_data)
        return docs

    def cloes(self):
        pass

def main(argv):
    dr = KafkaReader()
    while (True):
        docs = dr.read_docs()
        print(len(docs))
        if len(docs) > 0:
            print(docs[0])
        time.sleep(5)


if __name__ == "__main__":
    main(sys.argv)
