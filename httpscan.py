#! /usr/bin/env python
# -*- coding: utf-8 -*-   

import re
import sys
import Queue
import threading
import optparse
import requests
from IPy import IP
import iplist
from bs4 import BeautifulSoup

TimeOut = 5  # request timeout

# User-Agent
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
    'Connection': 'close'}


class scan():
    def __init__(self, ip1, ip2, threads_num, port=None):
        self.threads_num = threads_num
        # self.cidr = IP(str(cidr), make_net=True)
        # build ip queue
        self.ip1 = ip1
        self.ip2 = ip2
        self.port = port
        # self.IPs = iplist.iplist('103.82.54.103', '103.82.54.110')  # 队列
        self.IPs = iplist.iplist(ip1, ip2)  # 队列
        # for ip in self.cidr:
        # ip = str(ip)
        # print cidr
        # self.IPs.put(cidr)  # 把IP写入队列

        self.ports = port.split(',')

    def request(self):
        while self.IPs.qsize() > 0:
            ip = self.IPs.get()
            for p in self.ports:

                str_ip = str(ip) + ":" +str(p)
                url = 'http://' + str_ip
                print url
                try:
                    r = requests.Session().get(url, headers=header, timeout=TimeOut)
                except:
                    continue
                r.coding = 'utf-8'

                status = r.status_code
                soup = BeautifulSoup(r.content, 'html.parser')
                if soup.title is None:
                    title = 'None'
                else:
                    title = soup.title.get_text()

                try:
                    banner = r.headers['Server']  # get the server banner
                except:
                    banner = 'None'

                # Save log

                print "|%-16s|%-6s|%-20s|%-30s|" % (ip, status, banner, title)
                print "+----------------+------+--------------------+------------------------------+"
                log_str = "IP:%s stats:%s server:%s title:%s" % (str_ip, status, banner, title)
                with open("./log/" + IP(self.ip1).strNormal(3) + ".log", 'a') as f:
                    f.write(log_str.encode('utf-8') + "\n")


if __name__ == "__main__":
    parser = optparse.OptionParser("Usage: %prog [options] target")
    parser.add_option("-t", "--thread", dest="threads_num",
                      default=10, type="int",
                      help="[optional]number of  theads,default=10")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(0)

    print "+----------------+------+--------------------+------------------------------+"
    print "|     IP         |Status|       Server       |            Title             |"
    print "+----------------+------+--------------------+------------------------------+"
    s = scan(ip1=args[0], ip2=args[1], port=args[2], threads_num=options.threads_num)
    s.request()
