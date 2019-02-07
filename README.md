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

* This application first needs a redis service in order to store result and queue awaiting benchmarks. This service name should start with `benchmark-redis-storage`

    ```bash
    cf create-service redis plan benchmark-redis-storage
    ```
* Other services you will bind to your application will be benched, be careful as bench may resul in data loss
* You need to have **pip3** installed to download vendor packages
* You need to be logged in your org/space and ready to **cf push**

# Usage

## API

### summary

API exposes 2 routes :

* /run : will add an entry in redis queue to start benchmarks. 
* /results : returns JSON object containing benchmarks results
* /metrics (`to be implemented`) : returns results in prometheus format

### configuration

API needs to be binded to `benchmark-redis-storage`, otherwise it will fail.  
API will look for external services and will dynamically configure itself, if it doesn't find any external services in addition to `benchmark-redis-storage`, it will fail.

## Worker

### summary

backend reads the queue and runs benchmarks

### configuration

Worker needs to be binded to `benchmark-redis-storage`, otherwise it will fail.  
Worker will look for external services and will dynamically configure itself, if it doesn't find any external services in addition to `benchmark-redis-storage`, it will fail.
