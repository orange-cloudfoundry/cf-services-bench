# -*- encoding: utf-8; -*-
import os
from celery import Celery
from .config import Config
from .model import RedisWrapper
from .results import upsert_result
import json

config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery('tasks', broker=redis_uri)


@celery.task
def bench(service, service_instance, scenario, token):
    result = 'blablabla'
    upsert_result(config, service,
                  service_instance['name'], scenario, token, result)
