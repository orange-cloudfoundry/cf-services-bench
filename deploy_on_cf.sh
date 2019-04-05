#!/bin/bash
#### Description: Creates needed deployment files for cf_services_bench and push it to CF
#### Written by: Axel FAUVEL - axel.fauvel@orange.com

CF_INSTANCE_MEMORY=128M
CF_INSTANCES=1
CF_BUILDPACK=python_buildpack
CF_PYTHON_VERSION=3.6.8
CF_PYTHON_DOWNLOAD_PACKAGES_LOCALY=0


APP_NAME=cf_services_bench
APP_SCENARIO=nominal
APP_REDIS_STORAGE=benchmark-redis-storage
# APP_SERVICES_TO_BENCH MUST be space separated
APP_SERVICES_TO_BENCH="p-mysql-bench"
APP_DONT_USE_REDIS_BENCHMARK=0

SEPARATOR=#######################################

if [ "$CF_PYTHON_DOWNLOAD_PACKAGES_LOCALY" == 1 ];then
  echo $SEPARATOR
  echo 'downloading packages'
  pip3 download -d app/vendor -r app/requirements.txt --no-binary=:all:
fi

echo $SEPARATOR
echo 'Setting Python version'
cat << EOF > app/runtime.txt
python-${CF_PYTHON_VERSION}
EOF

echo $SEPARATOR
echo 'Generating API deployment files'
cat << EOF > app/.cfignore
bin/
lib/*.lua
lib/*.so.*
lib/*.so
*pycache*
EOF

cat << EOF > manifest.yml
name: ${APP_NAME}_api
memory: $CF_INSTANCE_MEMORY
instances: $CF_INSTANCES
buildpack: $CF_BUILDPACK
path: app/
env:
  SCENARIO: $APP_SCENARIO
services:
  - $APP_REDIS_STORAGE
$(for service in $(echo $APP_SERVICES_TO_BENCH);do echo "  - $service";done)
EOF

cat << EOF > app/Procfile
web: python -m cf_services_bench
EOF

echo $SEPARATOR
echo 'Deploying API'
cf push


echo $SEPARATOR
echo 'Generating worker deployment files'
rm app/.cfignore

cat << EOF > manifest.yml
name: ${APP_NAME}_worker
memory: $CF_INSTANCE_MEMORY
instances: $CF_INSTANCES
buildpack: $CF_BUILDPACK
path: app/
env:
  SCENARIO: $APP_SCENARIO
  LD_LIBRARY_PATH: /home/vcap/app/lib/
  LUA_PATH: /home/vcap/app/lib/oltp_common.lua
$(if [ "$APP_DONT_USE_REDIS_BENCHMARK" == 1 ];then echo "  DONT_USE_REDIS_BENCHMARK: 1";fi)
services:
  - $APP_REDIS_STORAGE
$(for service in $(echo $APP_SERVICES_TO_BENCH);do echo "  - $service";done)
EOF

echo $SEPARATOR
echo 'Deploying worker'
cf push -c "celery -A cf_services_bench.lib.tasks worker --loglevel=info" --health-check-type none
