# -*- encoding: utf-8; -*-
import os
from copy import deepcopy

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

        self.hostname, self.port = redis_uri.split("@")[1].split(":")
        self.password = redis_uri.split("@")[0].split("//")[1][1:]

        local = os.environ.get("LOCAL", False)
        use_redis_benchmark = not os.environ.get(
            "DONT_USE_REDIS_BENCHMARK", False)

        if local and use_redis_benchmark:
            self.cmd = sh.Command("/usr/bin/redis-benchmark")
        elif local and not use_redis_benchmark:
            self.cmd = sh.Command("/usr/bin/python")
        elif not local and use_redis_benchmark:
            self.cmd = sh.Command("/home/vcap/app/bin/redis-benchmark")
        elif not local and not use_redis_benchmark:
            self.cmd = sh.Command("/home/vcap/deps/0/python/bin/python")

        if scenario == "nominal":
            self.options = [
                "-h",
                self.hostname,
                "-p",
                self.port,
                "-a",
                self.password,
                "-n",
                "1000",
                "--csv",
            ]
        elif scenario == "benchmark":
            raise NotImplementedTest(
                "Benchmark is not yet implemented for Redis"
            )
        if not use_redis_benchmark:
            self.options.insert(0, "/home/vcap/app/bin/redis-bench.py")

    def _format_results(self):
        """
        results are JSON formated, recreating a list and trashing last line
        """

        results = deepcopy(self.raw_result.decode("utf-8").replace('"', ""))
        for element in results.split("\n"):
            if element:
                key, value = element.split(",")
                self.results[key] = value
