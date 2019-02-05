# -*- encoding: utf-8; -*-

import redis
import json


class RedisWrapper():
    def __init__(self, redis_uri):
        self.conn = redis.from_url(redis_uri)

    def set_kv(self, key, value, ttl=2000):
        self.conn.set(key, value, ex=ttl)

    def get(self, key):
        return self.conn.get(key)

    def get_last_result(self, key_prefix):
        pattern = '{}*'.format(key_prefix)
        keys = self.conn.keys(pattern)
        keys.sort()
        result = self.get(keys[-1])
        return json.loads(result)
