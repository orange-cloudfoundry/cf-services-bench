# -*- encoding: utf-8; -*-
import os
from celery import Celery
from .config import Config
from .model import RedisWrapper
from .results import upsert_result
from ..bench.redis import BenchRedis
import json

config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery('tasks', broker=redis_uri)


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

    if service == 'redis':
        bench = BenchRedis(service_instance['credentials']['uri'], scenario)
    elif service in ['mariadb', 'mysql']:
        upsert_result(config, service, service_instance['name'], scenario,
                      token, {'error': 'not implemented'})
        return False

    bench.run_bench()
    upsert_result(config, service,
                  service_instance['name'], scenario, token, bench.results)
