#!/bin/env python
# -*- coding:utf8 -*-

import argparse
from multiprocessing import Process
import config
from parsers import Parser


def work(role_id, params):
    parser = Parser(role_id, params)
    parser.run()
    pass


def start_multi_worker(params):
    workers = []
    for i in range(params["worker_number"]):
        p = Process(target=work, args=(i, params))
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
        params = config.parser_online
    elif args.mode == "test":
        params = config.parser_test
    else:
        raise Exception("not support mode {}".format(args.mode))
    start_multi_worker(params)


if __name__ == '__main__':
    main()
