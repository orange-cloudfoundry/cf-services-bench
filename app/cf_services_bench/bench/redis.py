# -*- encoding: utf-8; -*-
import os
import time
from copy import deepcopy

from pwgen import pwgen
import redis
import sh
from sh import ErrorReturnCode

from . import Bench
from ..lib.errors import NotImplementedTest


class BenchRedis(Bench):
    def __init__(self, redis_uri, scenario):
        """
        [summary]

        Arguments:
            Bench {[object]} -- Herited Bench object
            redis_uri {[type]} -- standard redis uri
            scenario {[type]} -- bench scenario

        Raises:
            NotImplementedTest -- [description]
        """
        self.raw_result = None
        self.results = {}
        self.uri = redis_uri
        self.hostname, self.port = redis_uri.split("@")[1].split(":")
        self.password = redis_uri.split("@")[0].split("//")[1][1:]
        self.uri = redis_uri

        self.local = os.environ.get("LOCAL", False)
        self.use_redis_benchmark = not os.environ.get(
            "DONT_USE_REDIS_BENCHMARK", False)
        self.query_count = 1000

        if self.use_redis_benchmark:
            if self.local:
                self.cmd = sh.Command("/usr/bin/redis-benchmark")
            elif not self.local:
                self.cmd = sh.Command("/home/vcap/app/bin/redis-benchmark")

            if scenario == "nominal":
                self.options = [
                    "-h",
                    self.hostname,
                    "-p",
                    self.port,
                    "-a",
                    self.password,
                    "-n",
                    self.query_count,
                    "--csv",
                ]
            elif scenario == "benchmark":
                raise NotImplementedTest(
                    "Benchmark is not yet implemented for Redis"
                )
        elif not self.use_redis_benchmark:
            self.conn = redis.from_url(self.uri)
            self.key_length = 64
            self.value_length = 1024
            self.ttl = 1

    def _format_results(self):
        """
        results are JSON formated, recreating a list and trashing last line
        """

        results = deepcopy(self.raw_result.decode("utf-8").replace('"', ""))
        for element in results.split("\n"):
            if element:
                key, value = element.split(",")
                self.results[key] = value

    def bench_get(self):
        bench_id = pwgen(64)
        # bench preparation
        for i in range(self.query_count):
            key = '{}-{}'.format(bench_id, i)
            self.conn.set(key, pwgen(
                self.value_length), ex=60)
        # real bench
        start_time = time.time()
        for i in range(self.query_count):
            key = '{}-{}'.format(bench_id, i)
            self.conn.get(key)
        result = round(time.time() - start_time, 2)
        self.results['GET']['time'] = result
        self.results['GET']['qps'] = round(self.query_count / result)

    def bench_set(self):
        bench_id = pwgen(64)
        start_time = time.time()
        for _ in range(self.query_count):
            key = '{}-{}'.format(bench_id, self.key_length)
            self.conn.set(key, pwgen(
                self.value_length), ex=self.ttl)
        result = round(time.time() - start_time, 2)
        self.results['SET']['time'] = result
        self.results['SET']['qps'] = round(self.query_count / result)

    def bench_ping(self):
        start_time = time.time()
        for _ in range(self.query_count):
            self.conn.ping()
        result = round(time.time() - start_time, 2)
        self.results['PING']['time'] = result
        self.results['PING']['qps'] = round(self.query_count / result)

    def bench(self):
        self.results['queries'] = self.query_count
        self.results['key_length'] = self.key_length
        self.results['value_length'] = self.value_length
        self.results['GET'] = {}
        self.results['SET'] = {}
        self.results['PING'] = {}
        self.bench_ping()
        self.bench_set()
        self.bench_get()

    def run_bench(self):
        """runs benchmark using cmd options
        if your bench returns an error code, stderr will be stored in 
        results.
        """
        if self.use_redis_benchmark:
            try:
                run = self.cmd(self.options)
                self.raw_result = run.stdout
                self._format_results()
            except sh.ErrorReturnCode as output:
                self.raw_result = str(output.stderr)
                self.results["error"] = self.raw_result
        elif not self.use_redis_benchmark:
            self.bench()
