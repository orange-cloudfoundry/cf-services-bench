# -*- encoding: utf-8; -*-
import json
import os

from celery import Celery

from ..bench.mysql import BenchMysql
from ..bench.redis import BenchRedis
from .config import Config
from .model import RedisWrapper
from .results import upsert_result

config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery("tasks", broker=redis_uri)


@celery.task
def bench(service, service_instance, scenario, token):
    """task that run benchs on services

    Arguments:
        service {[str]} -- [service that will be benched (redis, mysql...)]
        service_instance {[dict]} -- [credentials extracted from VCAP_SERVICES]
        scenario {[str]} -- [bench scenario to run can be nominal or benchmark]
        token {[str]} -- [unique token to identify bench session]

    Returns:
        [None] -- [description]
    """

    if service.lower().startswith("redis", "p-redis"):
        bench = BenchRedis(service_instance["credentials"]["uri"], scenario)

    elif service.lower().startswith(("p-mysql")):
#    elif service.lower().startswith(("mariadb", "mysql", "xtradb", "p-mysql")):
        bench = BenchMysql(service_instance["credentials"]["uri"], scenario)

    elif service.lower().startswith("user-provided"):
        if service_instance['tags'].lower().startswith((
                "mariadb", "mysql", "xtradb")):
            bench = BenchMysql(
                service_instance["credentials"]["uri"], scenario)
        elif service_instance['tags'].lower().startswith('redis'):
            bench = BenchRedis(
                service_instance["credentials"]["uri"], scenario)

    bench.run_bench()
    upsert_result(
        config,
        service,
        service_instance["name"],
        scenario,
        token,
        bench.results,
    )
