#                RPS.py
###        Rotating Proxy Server
####	1.Crawling public proxies lists from internet and save as a list.
####	2.Provide a local HTTP Proxy Interface, forwarding your every request via different HTTP Proxies
####	Can be useful to 'bypass' any Bans on IP from the website's firewall



```
usage: RPS.py [-h] [--ip IP] [--port PORT] [--page PAGE] [--delay DELAY]
              [--timeout TIMEOUT] [--log LOG] [--listname LISTNAME]
              [--uselist] [--foriegn]

optional arguments:
  -h, --help           show this help message and exit
  --ip IP              Address to Listen on.            Default: 127.0.0.1
  --port PORT          Port to Run on.          Default: 8899
  --page PAGE          Pages to Crawl Proxy.            Default: 1
  --delay DELAY        Max Delay of Proxies[second].    Default: 0.4
  --timeout TIMEOUT    Timeout of each Request[second]. Default: 7
  --log LOG            Logfile Name                     Default: proxy.log
  --listname LISTNAME  Proxy List File Name[careful]    Default: proxylist.txt
  --uselist            Use Private Proxy list instead of fetch online.[sepcify with --listname] Default: OFF
  --foriegn            Get Foriegn Proxy.[Very SLOW]    Default: OFF

```

###DKing@0-Sec


