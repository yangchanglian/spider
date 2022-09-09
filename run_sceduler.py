#!/bin/env python
# -*- coding:utf8 -*-

import sys, os
import argparse
import config
import logging
from scheduler import Scheduler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", type=str, default="test", help="online mode or test mode")
    args = parser.parse_args()
    if args.mode == "online":
        params = config.scheduler_online
    elif args.mode == "test":
        params = config.scheduler_test
    else:
        raise Exception("not support mode {}".format(args.mode))
    logging.basicConfig(
        format="[ %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d %(name)s ] %(message)s",
        datefmt="%y%m%d %H:%M:%S",
        level=logging.INFO,
        filename="./logs/scheduler.log")
    scheduler = Scheduler(params)
    scheduler.run()

if __name__ == "__main__":
    main()