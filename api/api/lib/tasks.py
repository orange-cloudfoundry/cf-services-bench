# -*- encoding: utf-8; -*-
from celery import Celery
from .config import Config

config = Config()
redis_uri = config.get_redis_storage_uri()
celery = Celery('tasks', broker=redis_uri)


@celery.task
def ma_tache():
    print('toto')
