'''
Rotating Proxy Server
DKing@0-Sec
'''
import sys,os,time,random,select  
import threading  
import logging  
import urllib2,socket
import argparse
import re

timeout = 7
maxConnetions = 200  
proxies = []
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}

def pickup_proxy():
    return random.choice(proxies).split(':')
    

def fetchproxy(url,reg,delay):
    logging.info("Fetching Proxies @ %s",url)
    try:
        req = urllib2.Request(url,None,header)
    except:
        print("Failed to fetch proxies @ %s",url)
        sys.exit
    response = urllib2.urlopen(req)
    html = response.read()
    p = re.compile(reg)
    proxy_list = p.findall(html)
    if len(proxy_list) > 0:
            for each_proxy in proxy_list[1:]:
                if len(each_proxy) == 4:
                    if each_proxy[2] == 'HTTP' and float(each_proxy[3]) < delay :
                        p_ip=(each_proxy[0]+':'+each_proxy[1])
                        proxies.append(p_ip)
                if len(each_proxy) == 3:
                    if each_proxy[2] == 'HTTP':
                        p_ip=(each_proxy[0]+':'+each_proxy[1])
                        proxies.append(p_ip)

    else:
        logging.error("Failed to match any proxies @ %s , Please manually check the RegEx pattern",url)
        sys.exit
  

def proxypool(page,delay,foriegn):
    logging.info("Fetching Proxies...")
    fp=open('proxylist.txt','w')

    ###http://www.xicidaili.com/        # Unrecommended due to safety
    #http://www.xicidaili.com/nn/
    #http://www.xicidaili.com/wn/

    reg_index=r'<td>(\d+\.\d+\.\d+\.\d+)</td>\n\s+<td>(\d{2,5})</td>\n\s+<td>.{2,10}?</td>\n\s+<td \bclass="country">.{2,6}?</td>\n\s+<td>(.{4,8})?</td>'
    reg_list_local=r'<td>(\d+\.\d+\.\d+\.\d+)</td>\n\s+<td>(\d{2,5})</td>\n\s+<td>\n\s+.{30,50}?</a>\n\s+</td>\n\s+<td \bclass="country">.{2,6}?</td>\n\s+<td>(.{4,8})?</td>\n\s+<td\sclass="country">\n\s+<div\stitle="(...).....?"\sclass="bar">'
    reg_list_forg=r'<td>(\d+\.\d+\.\d+\.\d+)</td>\n\s+<td>(\d{2,5})</td>\n\s+<td>\n\s+.{2,20}?\n\s+</td>\n\s+<td \bclass="country">.{2,6}?</td>\n\s+<td>(.{4,8})?</td>\n\s+<td\sclass="country">\n\s+<div\stitle="(...).....?"\sclass="bar">'
    
    for i in range(page):
        fetchproxy("http://www.xicidaili.com/nn/"+str(page),reg_list_local,delay)
        if foriegn == True:
            fetchproxy("http://www.xicidaili.com/wn/"+str(page),reg_list_forg,delay)

    for eachline in proxies:
        fp.write(eachline+'\n')
    fp.close()
    logging.info("Finished Fetching Proxies")


class Proxy:   
    def __init__(self, addr):   
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        self.proxy.bind(addr)   
        self.proxy.listen(maxConnetions)   
        self.inputs = {self.proxy:None}   
        self.route = {}   
     
    def serve_forever(self):   
        while 1:   
            readable, _, _ = select.select(list(self.inputs.keys()), [], [])   
            for self.sock in readable:   
                if self.sock == self.proxy:   
                    self.on_join()   
                else:  
                    try:  
                        data = self.sock.recv(81920)  
                    except Exception, e:  
                        logging.error(str(e))  
                        self.on_quit()  
                        continue  
                      
                    if not data:   
                        self.on_quit()   
                    else:  
                        try:  
                            self.route[self.sock].send(data)  
                        except Exception, e:  
                            logging.error(str(e))  
                            self.on_quit()  
                            continue  
     
    def on_join(self):   
        client, addr = self.proxy.accept()
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        try: 
            subproxy_ip,subproxy_port=pickup_proxy()
            subproxy_port=int(subproxy_port)
            forward.settimeout(timeout)
            forward.connect((subproxy_ip,subproxy_port))
            logging.info("%s:%d Forwarding success",subproxy_ip,subproxy_port)
        except Exception, e:  
            logging.error('%s:%d Error ... Switching to a New Proxy',subproxy_ip,subproxy_port)  
            client.close()  
            return  
        self.inputs [client] = None  
        self.inputs [forward] = None  
  
  
        self.route[client] = forward   
        self.route[forward] = client   

    def on_quit(self):  
        ls = [self.sock]  
        if self.sock in self.route:  
            ls.append(self.route[self.sock])  
        for s in ls:  
            if s in self.inputs:  
                del self.inputs[s]  
            if s in self.route:  
                del self.route[s]   
            s.close()   
              
 
def main():
    if len(sys.argv) == 1:
        print('\n#python RPS.py -h      for more options\n')

    parser = argparse.ArgumentParser(
        description='\t\tRPS.py\n\tRotating Proxy Server\nProvide a local HTTP Proxy Interface, forwarding your every request via different HTTP Proxies\nCan be useful to \'bypass\' any Bans on IP from the website\'s firewall',
        epilog='\nDKing@0-Sec',
        prefix_chars='-/+',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.format_help
    parser.add_argument('--ip', type=str,default='127.0.0.1', help='Address to Listen on.\t\tDefault: 127.0.0.1')
    parser.add_argument('--port',type=int,default=8899, help='Port to Run on.\t\tDefault: 8899')
    parser.add_argument('--page',type=int, default=1, help='Pages to Crawl Proxy.\t\tDefault: 1')
    parser.add_argument('--delay', type=float, default=0.4, help='Max Delay of Proxies[second].\tDefault: 0.4')
    parser.add_argument('--timeout', type=float, default=7, help='Timeout of each Request[second].\tDefault: 7')
    parser.add_argument('--log', type=str,default='proxy.log', help='Logfile Name\t\t\tDefault: proxy.log')
    parser.add_argument('--listname', type=str,default='proxylist.txt', help='Proxy List File Name[careful]\tDefault: proxylist.txt')
    parser.add_argument('--uselist',action='store_true',default=False, help='Use Private Proxy list instead of fetch online.[sepcify with --listname]\tDefault: OFF')
    parser.add_argument('--foriegn',action='store_true',default=False, help='Get Foriegn Proxy.[Very SLOW]\tDefault: OFF')
    args = parser.parse_args()

    timeout=args.timeout

    logging.basicConfig(level=logging.DEBUG,
              format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
              datefmt='%m-%d %H:%M',
              filename=args.log,
              filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-5s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


    if args.uselist == True:
            logging.info("Using Existing Proxy List")
            for pline in open(args.listname,'r'):
                proxies.append(pline)

    elif os.path.exists(args.listname) and time.time() - os.path.getmtime(args.listname) < 300 and os.path.getsize(args.listname) != 0:
            logging.info("Using cached Proxy List")
            for pline in open(args.listname,'r'):
                proxies.append(pline)
    else:
        logging.info("Proxies Expired. Fetching New Ones")
        proxypool(args.page,args.delay,args.foriegn)

    logging.info("Fetched %d Proxies in Total",len(proxies))
    try:
        logging.info("Listening on %s:%d",args.ip ,args.port)
        Proxy((args.ip, args.port)).serve_forever()  
    except KeyboardInterrupt, e:   
        logging.error("User Exited" + str(e))  

if __name__ == "__main__":
    main()