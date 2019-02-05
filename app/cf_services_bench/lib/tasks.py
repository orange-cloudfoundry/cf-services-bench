# -*- encoding: utf-8; -*-
import os
from celery import Celery
from .config import Config
from .model import RedisWrapper
import json

config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery('tasks', broker=redis_uri)


@celery.task
def bench(service, service_instance, scenario, token):
    session_result = {'service': service,
                      'service_instance': service_instance,
                      'scenario': scenario}
    redis_conn = RedisWrapper(redis_uri)
    key = '{}{}'.format(config.redis_key_prefix, token)

    previous_result = redis_conn.get(key)
    if previous_result:
        result = json.loads(previous_result.decode('utf-8'))
        result.append(session_result)
    else:
        result = [session_result]
    redis_conn.set_kv(key, json.dumps(result))
