#!/usr/bin/env python
# coding:utf-8
# Author: Zeroh

import re
import sys
import Queue
import threading
import optparse
import requests
from IPy import IP
import iplist

printLock = threading.Semaphore(1)  # lock Screen print
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

    def request(self):
        with threading.Lock():
            while self.IPs.qsize() > 0:
                ip = self.IPs.get()
                # print ip
                try:
                    if (self.port):
                        str_port = ":" + str(self.port)
                    else:
                        str_port = ""
                    url = 'http://' + str(ip) + str(str_port)
                    print url
                    r = requests.Session().get(url, headers=header, timeout=TimeOut)
                    status = r.status_code
                    title = re.search(r'<title>(.*)</title>', r.text)  # get the title
                    if title:
                        title = title.group(1)
                        print title
                    else:
                        title = "None"
                    banner = ''
                    banner += r.headers['Server'][:20]  # get the server banner
                    # Save log
                    log_str = "IP:%s 状态:%s 服务器:%s 标题:%s" % (ip, status, banner, title)
                    print log_str
                    with open("./log/" + IP(self.ip1).strNormal(3) + ".log", 'a') as f:
                        f.write(log_str + "\n")

                    printLock.acquire()
                    print "|%-16s|%-6s|%-20s|%-30s|" % (ip, status, banner, title)
                    print "+----------------+------+--------------------+------------------------------+"


                except Exception, e:
                    printLock.acquire()
                finally:
                    printLock.release()

    # Multi thread
    def run(self):
        for i in range(self.threads_num):
            t = threading.Thread(target=self.request)
            t.start()


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
    s.run()
