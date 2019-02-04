cf_services_bench
===

# Summary

CF application to run bench scenarios on external services. Each service provides 2 scenarios, nominal & benchmark.  

Nominal scenario will launch a light test in order to check that your service works properly.
Benchmark scenario will launch a heavy test to benchmark your service.

Currently supported services :
* mysql using sysbench as a benchmark tool
* redis using redis-benchmark as a benchmark tool

# Installation

## pre-requisites

This application first needs a redis service in order to store result and queue awaiting benchmarks. This service name should start with `benchmark-redis-storage`

```bash
cf create-service redis plan benchmark-redis-storage
```

## api

### summary

API exposes 2 routes :
* /run/<test> : will add an entry in redis queue to start benchmarks. `test` will be nominal or benchmark
* /results : returns JSON object containing benchmarks results
* /metrics (`to be implemented`) : returns results in prometheus format

### configuration

API needs to be binded to `benchmark-redis-storage`, if not, it will fail.  
API will look for external services and will dynamically configure itself, if it doesn't find any external
services in addition to `benchmark-redis-storage`, it will fail.

## backend

### summary

backend reads the queue and runs benchmarks

### configuration

backend needs to be binded to `benchmark-redis-storage`, if not, it will fail.  
backend will look for external services and will dynamically configure itself, if it doesn't find any external
services in addition to `benchmark-redis-storage`, it will fail.

# Configuration

To make it work, you need to :
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/vcap/app/public/lib/
export LUA_PATH=/home/vcap/app/public/lib/oltp_common.lua
```

Run a test :
```
# test redis-benchmark
/home/vcap/app/public/bin/redis-benchmark -h 10.98.229.51 -p 1192 -a mtn3kxpm -n 10

# test sysbench
/home/vcap/app/public/bin/sysbench --mysql-host=10.98.229.54 --mysql-port=1046 --mysql-user=pjB9m4Vh --mysql-password=sTRcJlv46UhGbo8qhUOPl9FKFZFHtdff --mysql-db=T43Y9hHcFkCe4iIV /home/vcap/app/public/lib/oltp_insert.lua cleanup
```
