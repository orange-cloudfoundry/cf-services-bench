Hello world for bench application hosted in CF

To make it work, you need to :
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/vcap/app/public/lib/
export LUA_PATH=/home/vcap/app/public/lib/oltp_common.lua
```

