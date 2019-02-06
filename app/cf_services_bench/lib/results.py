# -*- encoding: utf-8; -*-
import json
import time
from .model import RedisWrapper


def upsert_result(config, service, service_instance_name, scenario, token,
                  result):
    """Stores results in redis. Check if result previously exists and update
    it if so

    Arguments:

        config {[object]} -- config object
        service {[str]} -- [service that will be benched (redis, mysql...)]
        service_instance {[dict]} -- [credentials extracted from VCAP_SERVICES]
        scenario {[str]} -- [bench scenario to run can be nominal or benchmark]    
        token {[str]} -- [unique token to identify bench session]
        result {[str or dict]} -- result that will be stored in redis
    """

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
    """returns last result formated in JSON

    Arguments:
        config {[object]} -- config object

    Returns:
        [JSON] -- last result
    """

    redis_conn = RedisWrapper(config.get_redis_storage_uri())
    return json.dumps(redis_conn.get_last_result(config.redis_key_prefix))
