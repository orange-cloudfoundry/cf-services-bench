#!/usr/bin/env python3
# -*- encoding: utf-8; -*-
from .lib.config import Config
from .lib.tasks import ma_tache
from flask import Flask, jsonify, make_response
import sys


def main(serve=True):
    """ Main function """
    app = Flask("cf_services_bench_api")

    @app.route("/run", methods=["GET"])
    def run_bench():
        ma_tache.apply_async()
        return make_response('OK', 200)

    @app.route("/results", methods=["GET"])
    def results():
        return make_response('OK', 200)

    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    config = Config()
    config.check_config()
    sys.exit(main())
