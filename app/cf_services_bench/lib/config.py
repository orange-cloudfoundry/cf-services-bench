# -*- encoding: utf-8; -*-
from copy import deepcopy
import json
import os

from .errors import (NoServicesFound, MissingService,
                     MissingEnvironmentVariable, IncorrectConfiguration)


class Config():
    def __init__(self):
        if os.environ.get('VCAP_SERVICES', False):
            self.services = json.loads(os.environ['VCAP_SERVICES'])
        else:
            self.services = False
        self.compatible_services = ['redis', 'mysql', 'mariadb']
        self.scenario = os.environ.get('SCENARIO', False)
        self.services_to_bench = self._remove_redis_storage_from_services()

    def _check_redis_storage(self):
        try:
            for service in self.services['redis']:
                if service['name'].startswith('benchmark-redis-storage'):
                    return True
        except KeyError:
            return False

    def _remove_redis_storage_from_services(self):
        services = deepcopy(self.services)
        for index, service in enumerate(services['redis']):
            if service['name'].startswith('benchmark-redis-storage'):
                # removing benchmark-redis-storage
                del(services['redis'][index])
        if not services['redis']:
            # if redis service is empty, remove key
            services.pop('redis')
        return services

    def _check_services_to_bench(self):
        for service in self.compatible_services:
            if not self.services_to_bench.get(service, False):
                continue
            return True
        return False

    def check_config(self):
        if not self.scenario:
            raise MissingEnvironmentVariable('SCENARIO is not defined')
        if self.scenario not in ['nominal', 'benchmark']:
            raise IncorrectConfiguration(
                'Scenario should be either nominal or benchmark')
        if not self.services:
            raise NoServicesFound('No services are bound to this application')
        # check benchmark-redis-storage exists
        if not self._check_redis_storage():
            raise MissingService('Missing benchmark-redis-storage, exiting')
        # check any other service exists
        if not self._check_services_to_bench():
            raise MissingService('no services to bench, exiting')

    def get_redis_storage_uri(self):
        try:
            for service in self.services['redis']:
                if service['name'].startswith('benchmark-redis-storage'):
                    return service['credentials']['uri']
        except KeyError:
            return False
