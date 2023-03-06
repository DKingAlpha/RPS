#  RPS.py
Rotating Proxy Server

# What it is
RPS is a TCP proxy gateway that routes traffic through a randomly selected endpoint proxy from a pre-defined list.

RPS is protocol-transparent. Which means, when endpoint proxies are all SOCKS5 protocol, gateway protocol should be set to SOCKS5 too. Similarly to HTTP/HTTPS.\
You should not mix different proxies together in a same list.

This tool can be used to bypass firewalls. However, it is intended for educational purposes only. Illegal or immoral behavior is not encouraged.


# Usage

```sh
usage: RPS.py [-h] [-l ADDRESS] [-p PORT] [--log LOG_PATH] [--bufsize BUF_SIZE] [--backlog BACKLOG] [-v] PROXY_LIST

Rotating Proxy Server

positional arguments:
  PROXY_LIST            Proxy list file, lines of "IP:PORT"

options:
  -h, --help            show this help message and exit
  -l ADDRESS, --listen ADDRESS
                        IP address to listen on (default: 127.0.0.1)
  -p PORT, --port PORT  Port to listen on (default: 1080)
  --log LOG_PATH        Log Path (default: RPS.log)
  --bufsize BUF_SIZE    Buffer size of each connection (default: 4096)
  --backlog BACKLOG     Socket backlog (default: 4096)
  -v, --verbose         Verbose mode (default: False)
```

### DKing@ZeroSec


