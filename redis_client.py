#!/usr/bin/python
# -*- coding:utf-8 -*-


from redis import Redis
import logging


class RedisClientException(Exception):
    pass


class RedisClient(object):
    def __init__(self, host='localhost', port=6379, db=0, socket_timeout=30, retry_count=3, password=None):
        self.logger = logging.getLogger("RedisClient")
        self.host = host
        self.port = port
        self.db = db
        self.timeout = socket_timeout
        self.retry_count = retry_count
        self.password = password
        self.connect()

    def connect(self):
        retry = self.retry_count
        rd = None
        while retry > 0:
            try:
                rd = Redis(host=self.host, port=self.port, db=self.db, socket_timeout=self.timeout, password=self.password)
                break
            except Exception as e:
                retry -= 1
                self.logger.error("Connect to Redis failed in Connect():%s" % self.host, exc_info=True)
                continue
        if retry > 0 and rd != None:
            self.logger.info("success connect redis")
            self.rd = rd
        else:
            raise RedisClientException("Failed to connect Redis db:%s:%d" % (self.host, self.port))
        return True

    # key is string and value is string too
    def set(self, key, value, ttl=-1):
        ret = False
        retry = self.retry_count
        while retry > 0:
            try:
                if ttl > 0:
                    self.rd.setex(key, value, ttl)
                else:
                    self.rd.set(key, value)
                ret = True
                break
            except Exception as e:
                retry -= 1
                self.logger.error("Retry %d times to Connect Redis in Set()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                ret = False
                continue

        return ret


    def get(self, key):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.get(key)
                #self.logger.info("get value {}: {}".format(key, value))
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value

    def lrange(self, key, start=0, end=-1):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.lrange(key, start, end)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        self.logger.debug(value)
        return value

    def scard(self, key):
        value = 0
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.scard(key)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in scard()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value

    def sadd(self, key, v):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.sadd(key, v)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value

    def sismember(self, key, v):
        ret = False
        retry = self.retry_count
        while retry > 0:
            try:
                ret = self.rd.sismember(key, v)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        if ret:
            return True
        else:
            return False

    def smembers(self, key):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.smembers(key)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value

    def srem(self, key, v):
        ret = False
        retry = self.retry_count
        while retry > 0:
            try:
                ret = self.rd.srem(key, v)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Delete()" % (self.retry_count - retry),
                                      exc_info=True)
                self.connect()
                continue

        if ret:
            return True
        else:
            return False


    def delete(self, key):
        ret = False
        retry = self.retry_count
        while retry > 0:
            try:
                ret = self.rd.delete(key)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Delete()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue

        if ret:
            return True
        else:
            return False

    def lpush(self, key, *v):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.lpush(key, *v)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value

    def expire(self, key, ttl):
        value = None
        retry = self.retry_count
        while retry > 0:
            try:
                value = self.rd.expire(key, ttl)
                break
            except Exception as e:
                retry -= 1
                self.logger.exception("Retry %d times to Connect Redis in Get()" % (self.retry_count - retry), exc_info=True)
                self.connect()
                continue
        return value