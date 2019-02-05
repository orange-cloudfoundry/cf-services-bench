#!/bin/bash
echo 'downloading packages'
pip3 download -d app/vendor -r app/requirements.txt

echo 'Generating API deployment files'
cat << EOF > app/.cfignore
bin/
lib/*.lua
lib/*.so.*
lib/*.so
*pycache*
EOF

cat << EOF > manifest.yml
name: cf_service_bench_api
memory: 128M
instances: 1
buildpack: python_buildpack
path: app/
env:
  SCENARIO: nominal
EOF

cat << EOF > app/Procfile
web: python -m cf_services_bench
EOF


echo 'Deploying API'
cf push

############

echo 'Generating worker deployment files'
rm app/.cfignore

cat << EOF > manifest.yml
name: cf_service_bench_worker
memory: 128M
instances: 1
buildpack: python_buildpack
path: app/
env:
  SCENARIO: nominal
EOF

echo 'Deploying worker'
cf push -c "celery -A cf_services_bench.lib.tasks worker --loglevel=info" --health-check-type none