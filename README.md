Hello world for bench application hosted in CF

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
