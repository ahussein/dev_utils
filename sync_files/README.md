# Sync Files
Sync files to remote servers, can have multiple local filesystem paths that maps to remote servers. The script take a configuration file in toml format

## Example config
```toml
[gig_js]
path = "/home/abdelrahman/work/gig/jumpscale/"
remote_path = "/opt/code/github/jumpscale/"
remote_server_cs = "root@192.168.193.252"

[tud]
path = "/home/abdelrahman/work/tud/"
remote_path = "/home/tud/workspace/tud/"
remote_server_cs = "tud@192.168.194.155"
```

