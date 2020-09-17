# Test Plan


## Dispatching an HTTP Request
```bash
# Load up the tunnel and the client:
TARGET=example.com PORT=80 docker-compose up

# Then, request the site using the client host:
docker-compose exec client curl http://127.0.0.1:8000/index.html -A "Mozilla/5.0"
```

Result: 
``` html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<meta http-equiv="Content-Language" content="en" />
	<meta name="viewport" content="width=device-width, initial-scale = 1, user-scalable = yes" />
...
..
```


## Dispatching an HTTPS Request

```bash
# Load up the tunnel and the client:
TARGET=stackoverflow.com PORT=443 docker-compose up

# Then, request the site using the client host:
docker-compose exec client curl https://127.0.0.1:8000/ --header 'Host: www.stackoverflow.com'  --insecure
```

Result: 
``` html
<!DOCTYPE html>
    <html class="html__responsive html__unpinned-leftnav">
    <head>
        <title>Stack Overflow - Where Developers Learn, Share, &amp; Build Careers</title>
...
..
```

## Dispatching an HTTPS Request to Invalid URI

```bash
# Load up the tunnel and the client:
TARGET=stackoverflow.com PORT=443 docker-compose up

# Then, request the site using the client host:
docker-compose exec client curl https://127.0.0.1:8000/not/valid/URI --header 'Host: www.stackoverflow.com'  --insecure
```

Result: 
``` html
<!DOCTYPE html>

    <html class="html__responsive">
    <head>
        <title>Page not found - Stack Overflow</title>
...
..
```

# Dispatching an HTTPS Request to Invalid Port
```bash
# Load up the tunnel and the client:
TARGET=stackoverflow.com PORT=1234 docker-compose up

# Then, request the site using the client host:
docker-compose exec client curl https://127.0.0.1:8000
```
The server tries to establish connection with `stackoverflow.com` at port `1234`, will hang until it will reach the its time limit.