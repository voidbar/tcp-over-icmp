
# TCP Over ICMP
Using these client and server scripts, one could tunnel TCP over ICMP using raw sockets.

# Installation
This python project is built with native python libraries, no special installation are needed.
Although this project can be run locally, one would rather use `docker` and `docker-compose` in order to simulate a separate client and tunnel servers.

## How to run

```bash
# The template for running the tunnel server and the client is as follows:

# HOST_TO_TUNNEL is the host we would like the client to reach. We are specifying this so that we could pass that to the `client.py` script.
TARGET={HOST_TO_TUNNEL} PORT={TARGET_PORT} docker-compose up

# We are telling the client (through the docker container) to send a GET request to the HOST_TO_TUNNEL with URI.
docker-compose exec client curl https://127.0.0.1:8000/{URI} --header 'Host: {HOST_TO_TUNNEL}'  --insecure
```

## Examples
```bash 
# Spawning a server and a client:
TARGET=ynet.co.il PORT=443 docker-compose up

# Sending a GET request to ynet through the tunnel!
docker-compose exec client curl https://127.0.0.1:8000/home/0,7340,L-8,00.html --header 'Host: www.ynet.co.il'  --insecure
```

```bash 
# Spawning a server and a client:
TARGET=stackoverflow.com PORT=443 docker-compose up

# Sending a GET request to stackoverflow through the tunnel!
docker-compose exec client curl https://127.0.0.1:8000/ --header 'Host: www.stackoverflow.com'  --insecure 
```

```bash 
# Spawning a server and a client:
TARGET=google.com PORT=443 docker-compose up

# Sending a GET request to stackoverflow through the tunnel!
docker-compose exec client curl https://127.0.0.1:8000/index.html --header 'Host: www.google.com'  --insecure
```