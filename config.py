#!/bin/env python
# -*- coding:utf8 -*-

spider_online = {
    "worker_number": 8,
}

spider_test = {
    "worker_number": 2,
    "max_requests": 5,
    "writer": {
        "fake": True
    },
    "reader": {
        "fake": True,
        "max_read_count": 3
    }
}

scheduler_online = {

}

scheduler_test = {
    "writer": {
        "fake": True
    },
    "reader": {
        "fake": True,
        "max_read_count": 3
    }
}

parser_online = {

}

parser_test = {
    "worker_number": 3,
    "result_writer": {
        "fake": True
    },
    "task_writer": {
        "fake": True
    },
    "reader": {
        "fake": True,
        "max_read_count": 3
    },
    "extractor_params": [
        {"name":"UrlExtractor"},
        {"name": "DetailExtractor"}
    ]
}