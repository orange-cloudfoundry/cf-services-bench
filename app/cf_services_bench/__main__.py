#!/usr/bin/env python3
# -*- encoding: utf-8; -*-
import sys
import time

from flask import Flask, jsonify, make_response

from .lib.config import Config
from .lib.model import RedisWrapper
from .lib.results import get_last_result_as_json
from .lib.tasks import bench


def main(config, serve=True):
    """ Main function """
    app = Flask("cf_services_bench")

    @app.route("/run", methods=["GET"])
    def run_bench():
        timestamp = time.time()
        for service in config.services_to_bench:
            if service in config.compatible_services:
                for service_instance in config.services_to_bench[service]:
                    bench.delay(
                        service, service_instance, config.scenario, timestamp
                    )
        return make_response("OK", 200)

    @app.route("/results", methods=["GET"])
    def results():
        return make_response(get_last_result_as_json(config), 200)

    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    config = Config()
    config.check_config()
    sys.exit(main(config))
