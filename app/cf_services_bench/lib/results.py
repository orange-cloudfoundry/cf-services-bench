import json
import time
from .model import RedisWrapper


def upsert_result(config, service, service_instance_name, scenario, token,
                  result):

    session_result = {'service': service,
                      'service_instance': service_instance_name,
                      'scenario': scenario,
                      'date': time.strftime("%a, %d %b %Y %H:%M:%S"),
                      'result': result}
    redis_conn = RedisWrapper(config.get_redis_storage_uri())
    key = '{}{}'.format(config.redis_key_prefix, token)

    previous_result = redis_conn.get(key)
    if previous_result:
        result = json.loads(previous_result.decode('utf-8'))
        result.append(session_result)
    else:
        result = [session_result]
    redis_conn.set_kv(key, json.dumps(result))


def get_last_result_as_json(config):
    redis_conn = RedisWrapper(config.get_redis_storage_uri())
    return json.dumps(redis_conn.get_last_result(config.redis_key_prefix))
