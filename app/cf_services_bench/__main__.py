#!/usr/bin/env python3
# -*- encoding: utf-8; -*-
import time
from .lib.config import Config
from .lib.tasks import bench
from .lib.model import RedisWrapper
from flask import Flask, jsonify, make_response
import sys


def main(config, serve=True):
    """ Main function """
    app = Flask("cf_services_bench_api")

    @app.route("/run", methods=["GET"])
    def run_bench():
        timestamp = time.time()
        for service in config.services_to_bench:
            if service in config.compatible_services:
                for service_instance in config.services_to_bench[service]:
                    bench.delay(service, service_instance,
                                config.scenario, timestamp)
        return make_response('OK', 200)

    @app.route("/results", methods=["GET"])
    def results():
        redis_conn = RedisWrapper(config.get_redis_storage_uri())
        return jsonify(redis_conn.get_last_result(config.redis_key_prefix))

    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    config = Config()
    config.check_config()
    sys.exit(main(config))
