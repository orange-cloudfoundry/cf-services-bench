# -*- encoding: utf-8; -*-
import os
import sh
from copy import deepcopy
from ..lib.errors import NotImplementedTest
from sh import ErrorReturnCode


class BenchRedis():
    def __init__(self, redis_uri, scenario):
        self.hostname, self.port = redis_uri.split('@')[1].split(':')
        self.password = redis_uri.split('@')[0].split('//')[1][1:]
        if not os.environ.get('LOCAL', False):
            self.cmd = sh.Command('/home/vcap/app/bin/redis-benchmark')
        else:
            self.cmd = sh.Command('/usr/bin/redis-benchmark')
        if scenario == 'nominal':
            self.options = ['-h', self.hostname, '-p',
                            self.port, '-a', self.password,
                            '-n', '1000', '--csv']
        elif scenario == 'benchmark':
            raise NotImplementedTest(
                'Benchmark is not yet implemented for Redis')
        self.raw_result = None
        self.results = {}

    def _format_results(self):
        results = deepcopy(
            self.raw_result.decode('utf-8').replace('"', ''))
        for element in results.split('\n'):
            if element:
                key, value = element.split(',')
                self.results[key] = value

    def run_bench(self):
        try:
            run = self.cmd(self.options)
            self.raw_result = run.stdout
            self._format_results()
        except sh.ErrorReturnCode as output:
            self.raw_result = str(output.stderr)
            self.results['error'] = self.raw_result
