# Summary

CF application to run bench scenarios on external services. Each service provides 2 scenarios, nominal & benchmark.  

**Nominal scenarios** will launch a light test in order to check that your service works properly.

**Benchmark scenarios** will launch a heavy test to benchmark your service.

Currently supported services :

* **mysql** using sysbench as a benchmark tool
* **redis** using redis-benchmark as a benchmark tool

Currently implemented scenarios :

* mysql : nominal
* redis : nominal

:warning: Please be advised that benchmarks need their own database, don't use a production database, it will result in dataloss. :warning:

# Installation

## pre-requisites

* This application first needs a redis service in order to store result and queue awaiting benchmarks. This service name should **start with** `benchmark-redis-storage`

    ```bash
    cf create-service redis plan benchmark-redis-storage
    ```
* Other services you will bind to your application will be benched, be careful as bench may resul in data loss
* You need to have **pip3** installed to download vendor packages
* You need to be logged in your org/space and ready to **cf push**

## configuration

* Open **deploy_on_cf.sh**
* Fill `APP_REDIS_STORAGE` with redis service you previously created
* Fill `APP_SERVICES_TO_BENCH` variable with services you wish to bench. If you want to bench multiple services, separate them with a space
* run `./deploy_on_cf.sh`

# Usage

API exposes 2 routes :

* /run : will add an entry in redis queue to start benchmarks.
* /results : returns JSON object containing benchmarks results
* /metrics (`to be implemented`) : returns results in prometheus format

Just curl `api_url`/run to start benchmarks, results will appear on `api_url`/results as soon as they are available.

If you run a new bench, it will create new results, and so on.

# Architecture

## API

API uses Flask & Celery to provide API and queuing

## worker

Worker uses Celery to run tasks