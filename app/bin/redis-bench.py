#!/usr/bin/env python3
# -*- encoding: utf-8; -*-
import argparse
import redis
import time
from pwgen import pwgen


def get_args():
    """
    parse args and return object
    :return:
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h",
                        "--host",
                        required=True,
                        help="redis hostname")
    parser.add_argument("-p",
                        "--port",
                        required=True,
                        help="redis port")
    parser.add_argument("-a",
                        "--password",
                        required=True,
                        help="redis password")
    parser.add_argument("-n",
                        "--key_count",
                        required=True,
                        help="key count")

    parser.add_argument("-c",
                        "--csv",
                        action="store_true",
                        help="Format output in csv")

    return parser.parse_args()


class RedisBenchmark:
    def __init__(self, host, port, password, key_count):
        self.conn = redis.Redis(host=host, port=port, password=password)
        self.key_count = int(key_count)
        self.key_length = 64
        self.value_length = 1024
        self.ttl = 1

    def _print_result(self, key, value):
        print('"{}","{}"'.format(key, value))

    def bench_get(self):
        bench_id = pwgen(64)
        # bench preparation
        for i in range(self.key_count):
            key = '{}-{}'.format(bench_id, i)
            self.conn.set(key, pwgen(
                self.value_length), ex=60)
        # real bench
        start_time = time.time()
        for i in range(self.key_count):
            key = '{}-{}'.format(bench_id, i)
            self.conn.get(key)
        result = time.time() - start_time
        self._print_result('GET', result)

    def bench_set(self):
        bench_id = pwgen(64)
        start_time = time.time()
        for _ in range(self.key_count):
            key = '{}-{}'.format(bench_id, self.key_length)
            self.conn.set(key, pwgen(
                self.value_length), ex=self.ttl)
        result = time.time() - start_time
        self._print_result('SET', result)

    def bench_ping(self):
        start_time = time.time()
        for _ in range(self.key_count):
            self.conn.ping()
        result = time.time() - start_time
        self._print_result('PING', result)

    def bench(self):
        self.bench_ping()
        self.bench_set()
        self.bench_get()


args = get_args()
da_bench = RedisBenchmark(args.host, args.port, args.password, args.key_count)
da_bench.bench()
