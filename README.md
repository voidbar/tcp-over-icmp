


## Examples

```bash
# Terminal 1 - Spawn a server:
sudo python server.py


# Terminal 2 - Spawn a server:
sudo python client.py --tunnel-host 192.168.1.15 --listen-port 8000 --target-host ynet.co.il --target-port 443

# Terminal 3 - Send a get request:
curl https://127.0.0.1:8000/home/0,7340,L-8,00.html --header "Host: www.ynet.co.il"  --insecure
```


```bash
# Terminal 1 - Spawn a server:
sudo python server.py


# Terminal 2 - Spawn a server:
sudo python client.py --tunnel-host 192.168.1.15 --listen-port 8000 --target-host stackoverflow.com --target-port 443

# Terminal 3 - Send a get request:
curl https://127.0.0.1:8000/index.html --header "Host: stackoverflow.com"  --insecure
```

```bash
# Terminal 1 - Spawn a server:
sudo python server.py


# Terminal 2 - Spawn a server:
sudo python client.py --tunnel-host 192.168.1.15 --listen-port 8000 --target-host www.google.com --target-port 80

# Terminal 3 - Send a get request:
curl http://127.0.0.1:8000/ --header "Host: www.google.com"
```