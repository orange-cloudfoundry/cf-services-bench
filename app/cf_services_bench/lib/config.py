# -*- encoding: utf-8; -*-
import json
import os
from copy import deepcopy

from .errors import (
    IncorrectConfiguration,
    MissingEnvironmentVariable,
    MissingService,
    NoServicesFound,
)


class Config:
    """Check and stores configuration needed

    Raises:
        MissingEnvironmentVariable -- [description]
        IncorrectConfiguration -- [description]
        NoServicesFound -- [description]
        MissingService -- [description]
        MissingService -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self):
        """[summary]
        """

        if os.environ.get("VCAP_SERVICES", False):
            self.services = json.loads(os.environ["VCAP_SERVICES"])
        else:
            raise NoServicesFound("No services are bound to this application")
        self.compatible_services = ("redis", "mysql", "mariadb")
        self.scenario = os.environ.get("SCENARIO", False)
        self.redis_key_prefix = "_redis_bench."
        self.redis_providers = self._get_redis_providers()
        self.services_to_bench = self._remove_redis_storage_from_services()

    def _get_redis_providers(self):
        """
        List all service providers and return only those that starts with redis
        """
        return [provider for provider in
                list(self.services.keys())
                if provider.lower().startswith('redis')]

    def _check_redis_storage(self):
        """checks that a redis service with name starting with
        benchmark-redis-storage exists

        Returns:
            [bool] -- [True or False depending on service existance]
        """
        try:
            for provider in self.redis_providers:
                for service in self.services[provider]:
                    if service["name"].startswith("benchmark-redis-storage"):
                        return True
        except KeyError:
            return False

    def _remove_redis_storage_from_services(self):
        """[summary]

        Returns:
            [dict] -- [returns a dict containing services excluding 
            benchmark-redis-storage]
        """

        services = deepcopy(self.services)
        for provider in self.redis_providers:
            for index, service in enumerate(services[provider]):
                if service["name"].startswith("benchmark-redis-storage"):
                    # removing benchmark-redis-storage
                    del (services[provider][index])
            if not services[provider]:
                # if redis service is empty, remove key
                services.pop(provider)
            return services

    def _check_services_to_bench(self):
        """checks existance of services to bench

        Returns:
            [bool] -- [description]
        """

        for service in self.compatible_services:
            for service_to_bench in self.services_to_bench.keys():
                if service_to_bench.lower().startswith(service):
                    return True

    def check_config(self):
        """checks that programm has a proper configuration

        Raises:
            MissingEnvironmentVariable -- [description]
            IncorrectConfiguration -- [description]
            NoServicesFound -- [description]
            MissingService -- [description]
            MissingService -- [description]
        """

        if not self.scenario:
            raise MissingEnvironmentVariable("SCENARIO is not defined")
        if self.scenario not in ["nominal", "benchmark"]:
            raise IncorrectConfiguration(
                "Scenario should be either nominal or benchmark"
            )
        if not self.services:
            raise NoServicesFound("No services are bound to this application")
        # check benchmark-redis-storage exists
        if not self._check_redis_storage():
            raise MissingService("Missing benchmark-redis-storage, exiting")
        # check any other service exists
        if not self._check_services_to_bench():
            raise MissingService("no services to bench, exiting")

    def get_redis_storage_uri(self):
        """extracts uri from benchmark-redis-storage

        Returns:
            [str] -- returns uri or False
        """

        try:
            for provider in self.redis_providers:
                for service in self.services[provider]:
                    if service["name"].startswith("benchmark-redis-storage"):
                        return service["credentials"]["uri"]
        except KeyError:
            return False
