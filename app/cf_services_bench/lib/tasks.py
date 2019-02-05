# -*- encoding: utf-8; -*-
import os
from celery import Celery
from .config import Config


config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery('tasks', broker=redis_uri)


@celery.task
def bench(service, service_instance, scenario):
    print('service: {}'.format(service))
    print('service_instance: {}'.format(service_instance))
    print('scenario: {}'.format(scenario))
