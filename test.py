#!/bin/env python
# -*- coding:utf8 -*-

import sys, os
import traceback
import aiohttp
import time
import base64
import zlib
import requests
import json

def request(request_data):
    try:
        with requests.session() as session:
            headers = request_data.get("headers", None)
            data = request_data.get("post_data", None)
            method = request_data["method"]
            url = request_data["url"]
            with session.request(method, url, data=data, headers=headers) as response:
                content = response.content
                status = response.status_code
                grab_time = int(time.time() * 1000)
                data = {"result_data": str(base64.b64encode(zlib.compress(content)), encoding="utf-8"),
                        "result_status": status, "grab_time": grab_time, "request_data": request_data}
                return data
    except Exception as e:
        traceback.print_exc()
        return None
def decompress(content):
    return str(zlib.decompress(base64.b64decode(bytes(content, encoding="utf-8"))), encoding="utf-8")

def main1(argv):
    request_data = {
        "headers": {"User-Agent": "Mozilla/5.0"},
        "method": "get",
        "url": "https://pubmed.ncbi.nlm.nih.gov/?term={}&page={}".format("cancer", 1)
    }
    data = request(request_data)
    json_data =json.dumps(data)
    print(json_data)
    print (decompress(data['result_data']))

def main(argv):
    import hashlib
    m = hashlib.sha256()
    m.update(bytes("123", encoding="utf-8"))
    print(m.hexdigest())
if __name__ == "__main__":
    firstSet = set({"name": "tyson", "age": "30"})
    print(firstSet)
    #main1(sys.argv)