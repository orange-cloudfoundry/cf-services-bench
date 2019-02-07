# -*- encoding: utf-8; -*-

import redis
import json
import time


class RedisWrapper:
    """Redis wrapper to store results

    Returns:
        [type] -- [description]
    """

    def __init__(self, redis_uri):
        self.conn = redis.from_url(redis_uri)

    def set_kv(self, key, value, ttl=604800):
        self.conn.set(key, value, ex=ttl)

    def get(self, key):
        return self.conn.get(key)

    def get_last_result(self, key_prefix):
        """Get all keys matching key_prefix pattern and returns last one
        alphabetically ordered

        Arguments:
            key_prefix {[str]} -- [key_prefix]

        Returns:
            [str] -- [last key alphabetically ordered]
        """

        pattern = "{}*".format(key_prefix)
        keys = self.conn.keys(pattern)
        keys.sort()
        result = self.get(keys[-1])
        return json.loads(result)
