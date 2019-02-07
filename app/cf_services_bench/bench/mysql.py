# -*- encoding: utf-8; -*-
import json
import os
from copy import deepcopy

import sh
from sh import ErrorReturnCode

from . import Bench
from ..lib.errors import NotImplementedTest

# Fill this variable only in LOCAL mode
_LOCAL_APP_PATH = "/home/afauvel/orange/gitlab/afauvel/cf_services_benchs/app"


class BenchMysql(Bench):
    def __init__(self, mysql_uri, scenario):
        """
        [summary]

        Arguments:
            Bench {[object]} -- Herited Bench object
            mysql_uri {[type]} -- standard mysql uri
            scenario {[type]} -- bench scenario

        Raises:
            NotImplementedTest -- [description]
        """
        self.raw_result = None
        self.results = {}

        self.hostname, self.port = (
            mysql_uri.split("@")[1].split("/")[0].split(":")
        )
        self.user, self.password = (
            mysql_uri.split("@")[0].split("//")[1].split(":")
        )

        self.database = mysql_uri.split("@")[1].split("/")[1].split("?")[0]

        if not os.environ.get("LOCAL", False):
            self.cmd = sh.Command("/home/vcap/app/bin/sysbench")
        else:
            self.cmd = sh.Command("{}/bin/sysbench".format(_LOCAL_APP_PATH))

        self.options = [
            "--mysql-user={}".format(self.user),
            "--mysql-host={}".format(self.hostname),
            "--mysql-port={}".format(self.port),
            "--mysql-password={}".format(self.password),
            "--mysql-db={}".format(self.database),
        ]

        if scenario == "nominal":
            if not os.environ.get("LOCAL", False):
                self.options.append("/home/vcap/app/lib/oltp_read_write.lua")
            else:
                self.options.append(
                    "{}/lib/oltp_read_write.lua".format(_LOCAL_APP_PATH)
                )
        elif scenario == "benchmark":
            raise NotImplementedTest(
                "Benchmark is not yet implemented for MySQL"
            )

        self.cleanup_options = self.options + ["cleanup"]
        self.prepare_options = self.options + ["prepare"]
        self.run_options = self.options + ["run"]

    def _format_results(self):
        """
        retrieving stdout json format by removing useless lines
        """
        results = deepcopy(self.raw_result.decode("utf-8").split("\n"))
        for index, element in enumerate(results):
            if element.startswith("  {"):
                self.results = json.loads("".join(results[index:-2]))
                break

    def run_bench(self):
        """runs benchmark using cmd options
        if your bench returns an error code, stderr will be stored in
        results.
        sysbench works in 3 steps : cleanup / prepare / run
        """

        try:
            cleanup = self.cmd(self.cleanup_options)
            cleanup.wait()
            prepare = self.cmd(self.prepare_options)
            prepare.wait()
            run = self.cmd(self.run_options)
            run.wait()
        except sh.ErrorReturnCode as output:
            self.raw_result = str(output.stderr)
            self.results["error"] = self.raw_result
            return False

        self.raw_result = run.stdout
        self._format_results()
