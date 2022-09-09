#!/bin/env python
# -*- coding:utf8 -*-

import sys
import os
import logging
from reader import KafkaReader
from writer import KafkaWriter
from reader import FakeReader
from writer import FakeWriter
from async_pool import AsyncPool
import json
import aiohttp
import time
import base64
import zlib


class Spider(object):
    """
    负责组装http请求，并爬取、存储数据
    除kafka组件外，其他进行了简单测试
    """
    def __init__(self, role_id, params):
        self.role_id = role_id
        self.params = params
        logging.basicConfig(
            format="[ %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d %(name)s ] %(message)s",
            datefmt="%y%m%d %H:%M:%S",
            level=logging.INFO,
            filename="./logs/spider.log.{}".format(role_id))
        self.logger = logging.getLogger("Spider.py")
        self.reader = FakeReader(self.logger, params["reader"]) if params["reader"].get(
            "fake") else KafkaReader(self.logger, params["reader"])
        self.writer = FakeWriter(self.logger, params["writer"]) if params["writer"].get(
            "fake") else KafkaWriter(self.logger, params["writer"])
        self.async_pool = AsyncPool(maxsize=params["max_requests"])

    @staticmethod
    def compress(content):
        return str(base64.b64encode(zlib.compress(bytes(content, encoding="utf-8"))), encoding="utf-8")

    async def request(self, request_data):
        try:
            async with aiohttp.ClientSession() as session:
                headers = request_data.get("headers", None)
                data = request_data.get("post_data", None)
                method = request_data["method"]
                url = request_data["url"]
                async with session.request(method, url, data=data, headers=headers) as response:
                    content = await response.text()
                    grab_time = int(time.time() * 1000)
                    data = {
                        "result_data": self.compress(content),
                        "result_status": response.status,
                        "grab_time": grab_time,
                        "request_data": request_data}
                    return data
        except Exception as e:
            self.logger.exception(
                "request data error: %s",
                json.dumps(request_data))
            return None

    def save_result(self, future):
        try:
            result = future.result()
            self.writer.write_one_json(result)
        except Exception as e:
            self.logger.exception("save_result excpetion:")
            return None

    def run(self):
        while True:
            try:
                docs = self.reader.read_docs()
                for doc in docs:
                    self.async_pool.add()
                    self.async_pool.submit(
                    self.request(doc), lambda x: self.save_result(x))
            except Exception as e:
                self.logger.exception("run doc error")

    def close(self):
        # 停止事件循环
        self.async_pool.release()

        # 等待
        self.async_pool.wait()

        # 停止输入输出
        self.reader.close()
        self.writer.close()


def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv)
