#!/bin/env python
# -*- coding:utf8 -*-

import sys
import logging
from reader import KafkaReader
from writer import KafkaWriter
from reader import FakeReader
from writer import FakeWriter
import time
import base64
import zlib
import hashlib
from redis_client import RedisClient


class Scheduler(object):
    """
    负责任务调度，去重，生成id等。
    任务较为简单设计为单进程模式，否则去重逻辑会较为复杂。
    20220904 暂时没有测试
    """
    def __init__(self, params):
        self.params = params
        self.logger = logging.getLogger("Spider.py")
        self.reader = FakeReader(self.logger, params["reader"]) if params["reader"].get(
            "fake") else KafkaReader(self.logger, params["reader"])
        self.writer = FakeWriter(self.logger, params["writer"]) if params["writer"].get(
            "fake") else KafkaWriter(self.logger, params["writer"])
        self.redis_client = RedisClient(**params["redis"])
        self.user_agent = params["user_agent"]
        self.speed_limit = params["speed_limit"] # 单位 毫秒/个

    def get_item_md5(self, doc):
        method = doc["method"]
        post_data = doc.get("post_data", "")
        url = doc["url"]
        source = doc["source"]
        m = hashlib.sha256()
        m.update(bytes("{}{}{}{}".format(source, method, url, post_data), encoding="utf-8"))
        return m.hexdigest()[:32]

    def fill_info(self, doc):
        headers = doc.get("headers", {})
        headers["User-Agent"] = self.user_agent
        doc["item_id"] = self.get_item_md5(doc)
        doc["headers"] = headers


    def run(self):
        last_time = 0
        while True:
            try:
                # docs like {"method": "get", "url": "https://pubmed.ncbi.nlm.nih.gov/?term=cancer&page=1"
                #            "source": "pubmed"}
                docs = self.reader.read_docs()
                for doc in docs:
                    self.fill_info(doc)
                    # 如果在redis查到说明已经爬取过, 则不处理
                    if self.redis_client.get(doc["item_id"]):
                        continue
                    else:
                        now = time.time()
                        if now - last_time < self.speed_limit:
                            time.sleep(now - last_time)
                        # 写入kafka 交给spider 进行爬取
                        if self.writer.write_one_json(doc):
                            # 在redis中记录
                            self.redis_client.set(doc["item_id"], int(now*1000))
                            last_time = now


            except Exception as e:
                self.logger.exception("run doc error: %s")



def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv)
