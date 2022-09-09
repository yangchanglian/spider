#!/bin/env python
# -*- coding:utf8 -*-


"""
用于并发爬取任务，支持多进程异步爬取。
从kafka读取人物，并将结果放回至kafka
"""

import argparse # 定位参数
from multiprocessing import Process
import config
import time
from spider import Spider

def work(role_id, params):
    spider = Spider(role_id, params)
    spider.run()
    pass


def start_multi_worker(params):
    workers = []
    for i in range(params["worker_number"]):
        p = Process(target=work, args=(i, params)) # 创建进程
        p.start()
        workers.append(p)
    for i, worker in enumerate(workers):
        worker.join()
        print("worker {} stop".format(i))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, default="test", help="online mode or test mode")
    args = parser.parse_args()
    if args.mode == "online":
        params = config.spider_online
    elif args.mode == "test":
        params = config.spider_test
    else:
        raise Exception("not support mode {}".format(args.mode))
    start_multi_worker(params)


if __name__ == '__main__':
    main()
