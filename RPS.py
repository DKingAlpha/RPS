#!/usr/bin/python3
#-*- coding: utf-8 -*-

import argparse
import signal
import socket
from concurrent.futures import ThreadPoolExecutor
import re
import logging
import random

def parse_args():
    parser = argparse.ArgumentParser(description='Rotating Proxy Server', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--listen', metavar='ADDRESS', default='127.0.0.1', help='IP address to listen on')
    parser.add_argument('-p', '--port', metavar='PORT', type=int, default=1080, help='Port to listen on')
    parser.add_argument('--log', metavar='LOG_PATH', default='RPS.log', help='Log Path')
    parser.add_argument('--bufsize', metavar='BUF_SIZE', type=int, default=4096, help='Buffer size of each connection')
    parser.add_argument('--backlog', metavar='BACKLOG', type=int, default=4096, help='Socket backlog')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    # positional arguments  
    parser.add_argument('proxylist', metavar='PROXY_LIST', help='Proxy list file, lines of "IP:PORT"')
    return parser.parse_args()

class ProxyPicker:
    def __init__(self, filename):
        self.proxies = []
        with open(filename, encoding='utf-8') as f:
            for line in f:
                result = self._parse_line(line)
                if result == False:
                    logging.error(f'Unknown proxy format: {line}')
                    continue
                self.proxies.append(result)
        logging.info(f'Loaded {len(self.proxies)} proxies from {filename}')

    def _parse_line(self, line:str):
        proxy = line.strip()
        if not proxy:
            return False
        if proxy.startswith('#'):
            return False
        if ':' not in proxy:
            return False
        if proxy.count(':') != 1:
            return False
        addr, port = proxy.split(':')
        if not addr or not port:
            return False
        if port.isdigit() == False or int(port) < 0 or int(port) > 65535:
            return False
        if not (re.match('^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', addr) or \
            re.match('^(([01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\.){3}([01]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])$', addr)):
            return False
        return (addr, int(port))

    def get_random_proxy(self):
        if len(self.proxies) == 0:
            return None
        return random.choice(self.proxies)

class ProxyServer:
    def __init__(self):
        self.args = parse_args()
        # server
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.args.listen, self.args.port))
        self.listener.listen(self.args.backlog)
        if self.args.verbose:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        # log
        logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=self.args.log,
                    filemode='w'
        )
        formatter = logging.Formatter('%(levelname)-5s %(message)s')
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info(f'Listening on {self.args.listen}:{self.args.port}, backlog={self.args.backlog}')
        ### after logging is configured

        self.proxypicker = ProxyPicker(self.args.proxylist)
        # threadpool
        self.threadpool = ThreadPoolExecutor(max_workers=self.args.backlog, thread_name_prefix='RPS')
        # loop
        self.running = False
        # ctrl-c handling
        def signal_handler(signal,frame):
            self.stop()
        signal.signal(signal.SIGINT, signal_handler)
    
    def stop(self):
        self.running = False
        self.listener.close()
        self.threadpool.shutdown(wait=True, cancel_futures=True)
        logging.info('ProxyServer is closed')
        logging.info('All threads are closed')


    def start(self):
        self.running = True
        while self.running:
            # Accept an incoming connection
            try:
                client_sock, client_addr = self.listener.accept()
            except Exception as e:
                if isinstance(e, OSError) and e.errno != 9:
                    logging.error(f'Error: Failed to accept connection: {e}')
                break
            logging.debug(f'Accepted connection from {client_addr[0]}:{client_addr[1]}')

            # Get a random proxy
            target = self.proxypicker.get_random_proxy()
            if target == None:
                logging.error(f'Error: No proxy available')
                client_sock.close()
                break
            target_host, target_port = target

            # Create a TCP socket to connect to the target proxy
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target_sock.connect((target_host, target_port))
            except Exception as e:
                logging.error(f'Error: Failed to connect to proxy at {target_host}:{target_port}: {e}')
                client_sock.close()
                continue

            # Forward data between the two sockets, non-deadlockingly
            logging.debug(f'Connected established {client_addr[0]}:{client_addr[1]} <-> {target_host}:{target_port}')
            self.threadpool.submit(self.handle_client, client_sock, target_sock)
            self.threadpool.submit(self.handle_client, target_sock, client_sock)
        logging.info('Stopped accepting new connections')


    def handle_client(self, client_sock: socket.socket, target_sock: socket.socket):
        # Handle incoming data from client_sock and forward it to target_sock
        while True:
            try:
                data = client_sock.recv(self.args.bufsize)
            except ConnectionError as e:
                break
            except Exception as e:
                logging.error(f'Connection Error: {client_sock}->{target_sock}: {e}')
                break
            if not data:
                break
            target_sock.sendall(data)

        # Close both sockets when done
        client_sock.close()
        target_sock.close()

if __name__ == '__main__':
    gateway = ProxyServer()
    gateway.start()

