# Several deprecated commands and the replacements you should be using

Software development is a field where things change at incredible speed; changes are made all the time due improvements in hardware and the surge of new environments.

For the same reason tools change, and sometimes they do not adapt well but eventually fade and get replaced by other tools (with the debatable point of the new tools being better than the previous ones).

I want to share with you a few tools that you may be still using and why you should switch to the better well known alternatives that can accomplish the same, if no more, while they are also well maintained.

So here is the list with no specific order.

# egrep and fgrep: Just learn to use grep

Ah, the venerable [grep](http://www.gnu.org/software/grep/); This is one of the best examples of the [philosophy of the Unix operating system](https://en.wikipedia.org/wiki/Unix_philosophy):

> Write programs that do one thing and do it well. Write programs to work together. Write programs to handle text streams, because that is a universal interface

**egrep** or 'extended grep' uses regular expressions to match a line. It also happens than it was deprecated in favor of using regular grep with a flag, ```grep -E```.

```shell=
[josevnz@macmini2 ~]$ egrep '^[fj]' /etc/passwd
ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
josevnz:x:1000:1000:josevnz:/home/josevnz:/bin/bash
[josevnz@macmini2 ~]$ grep -E '^[fj]' /etc/passwd
ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
josevnz:x:1000:3000:josevnz:/home/josevnz:/bin/bash
```

That matches the lines that start with the letter j or f on the /etc/passwd file.

Another example of solving the problem by adding a new flag is **fgrep**. The 'Fixed' grep uses a fixed string for matching (no optimizations, faster than a regexp) as opposed to '-E'; It was replaced by ```grep -F```

```shell=
[josevnz@macmini2 ~]$ fgrep 'josevnz' /etc/passwd
josevnz:x:1000:3000:josevnz:/home/josevnz:/bin/bash
[josevnz@macmini2 ~]$ grep -F 'josevnz' /etc/passwd
josevnz:x:1000:3000:josevnz:/home/josevnz:/bin/bash
```

## Why egrep and fgrep were replaced?

Makes more sense to have a tool that behaves very similar to support that functionality by using flags. Just need to know that grep with a flag can use regular expressions or exact search.

# nslookup: Still well and alive

Raise your hand if you were ever trying to get the IP address of a server like this:

```shell=
[josevnz@macmini2 ~]$ nslookup kodegeek.com
Server:		192.168.1.1
Address:	192.168.1.1#53

Non-authoritative answer:
Name:	kodegeek.com
Address: 50.63.7.206
```

An alternative for nslookup is ```dig```:

```shell=
[josevnz@macmini2 ~]$ dig @192.168.1.1 kodegeek.com A +noall +answer +nocmd
kodegeek.com.		600	IN	A	50.63.7.206
```

Or the interactive mode, below showing how to get the PTR record of the same server (reverse lookup, get the name of a server by providing the IP address):

```shell=
> set type=ptr
> 50.63.7.206
Server:		192.168.1.1
Address:	192.168.1.1#53

Non-authoritative answer:
206.7.63.50.in-addr.arpa	name = ip-50-63-7-206.ip.secureserver.net.

Authoritative answers can be found from:
```

Equivalent command in dig:


```shell=
[josevnz@macmini2 ~]$ dig -x @192.168.1.1 kodegeek.com +noall +answer +nocmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 22696
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;1.1.168.\@192.in-addr.arpa.	IN	PTR

;; AUTHORITY SECTION:
in-addr.arpa.		3549	IN	SOA	b.in-addr-servers.arpa. nstld.iana.org. 2022033331 1800 900 604800 3600

;; Query time: 24 msec
;; SERVER: 192.168.1.1#53(192.168.1.1)
;; WHEN: Tue May 17 05:08:21 EDT 2022
;; MSG SIZE  rcvd: 122

kodegeek.com.		600	IN	A	50.63.7.206
```

*Dig* can do things than nslookup cannot; for example you can request a DNS transfer of a domain zone (including all record types), for example to make a backup of your DNS domain:

```shell=
[josevnz@macmini2 ~]$ dig +short ns kodegeek.com
ns51.domaincontrol.com.
ns52.domaincontrol.com.
[josevnz@macmini2 ~]$ dig axfr kodegeek.com @ns51.domaincontrol.com.
# *Note:* In this case it won't work because kodegeek.com has a domain protection. But the domain in your intranet may work.
```

*Nslookup* can do things that dig cannot, like the nice interactive mode you saw earlier, which is very useful when you are exploring DNS domains. And is can also run in non-interactive mode. 

*So what is the main difference*? Dig uses the operating system resolver libraries (the libraries that perform address lookups on DNS) while Nslookup does not, so it may behave differently when resolving addresses.


## Why nslookup was replaced?

Nslookup was not replaced by dig or host. Per [Wikipedia](https://en.wikipedia.org/wiki/Nslookup):

> nslookup was a member of the BIND name server software. Early[when?] in the development of BIND 9, the Internet Systems Consortium planned to deprecate nslookup in favor of host and dig. This decision was reversed in 2004 with the release of BIND 9.3[1] and nslookup has been fully supported since then.

So **it is perfectly fine to use both**.

# nettools: ifconfig, nestat, route

```ifconfig``` is the tool that you can use to get information about your network interfaces, and change their behaviour:

```shell=
[josevnz@macmini2 ~]$ /sbin/ifconfig
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:43:f9:d0:b4  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

enp1s0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether 00:1f:f3:46:38:96  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 16  

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 30  bytes 1170 (1.1 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 30  bytes 1170 (1.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wls1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.16  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::ac00:48ea:c7a6:1488  prefixlen 64  scopeid 0x20<link>
        inet6 fd22:4e39:e630:1:6688:3ffd:ea5b:d9e9  prefixlen 64  scopeid 0x0<global>
        ether 00:23:6c:7b:db:ac  txqueuelen 1000  (Ethernet)
        RX packets 1115786  bytes 107099421 (102.1 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 548530  bytes 359598134 (342.9 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

ifconfig was replaced by ```ip```. Let's see how you can list your network interfaces using it:

```shell=
[josevnz@macmini2 ~]$ ip address 
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: enp1s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN group default qlen 1000
    link/ether 00:1f:f3:46:38:96 brd ff:ff:ff:ff:ff:ff
3: wls1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:23:6c:7b:db:ac brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.16/24 brd 192.168.1.255 scope global noprefixroute wls1
       valid_lft forever preferred_lft forever
    inet6 fd22:4e39:e630:1:6688:3ffd:ea5b:d9e9/64 scope global noprefixroute 
       valid_lft forever preferred_lft forever
    inet6 fe80::ac00:48ea:c7a6:1488/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
4: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:42:43:f9:d0:b4 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
```

Another useful tool is ```route```. Let's check the routing table:

```shell=
[josevnz@macmini2 ~]$ route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         192.168.1.1     0.0.0.0         UG    600    0        0 wls1
172.17.0.0      0.0.0.0         255.255.0.0     U     0      0        0 docker0
192.168.1.0     0.0.0.0         255.255.255.0   U     600    0        0 wls1
```

```ip``` can also show us the [routing table](https://en.wikipedia.org/wiki/Routing_table) (information how your machine can connect to other machines); Now you can see why this tool took over:

```shell=
[josevnz@macmini2 ~]$ ip route list
default via 192.168.1.1 dev wls1 proto static metric 600 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
192.168.1.0/24 dev wls1 proto kernel scope link src 192.168.1.16 metric 600 
```

Another one that got replaced is netstat; with nestat you can see the list of active connections among other things. For example, to see the list of active listening tcp connections on your servers, without name resolution

```shell
[josevnz@dmaf5 ~]$ /usr/bin/netstat --numeric --tcp --listen
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 192.168.122.1:53        0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:5355            0.0.0.0:*               LISTEN     
tcp6       0      0 :::22                   :::*                    LISTEN     
tcp6       0      0 ::1:631                 :::*                    LISTEN     
tcp6       0      0 :::9323                 :::*                    LISTEN     
tcp6       0      0 :::5355                 :::*                    LISTEN     
tcp6       0      0 :::9100                 :::*                    LISTEN     
```

In this case, the command `ss` is the replacement you are looking for:

```shell=
[josevnz@dmaf5 ~]$ ss --numeric --tcp --listen
State               Recv-Q               Send-Q                             Local Address:Port                             Peer Address:Port              Process              
LISTEN              0                    32                                 192.168.122.1:53                                    0.0.0.0:*                                      
LISTEN              0                    4096                               127.0.0.53%lo:53                                    0.0.0.0:*                                      
LISTEN              0                    128                                      0.0.0.0:22                                    0.0.0.0:*                                      
LISTEN              0                    128                                    127.0.0.1:631                                   0.0.0.0:*                                      
LISTEN              0                    4096                                     0.0.0.0:5355                                  0.0.0.0:*                                      
LISTEN              0                    128                                         [::]:22                                       [::]:*                                      
LISTEN              0                    128                                        [::1]:631                                      [::]:*                                      
LISTEN              0                    4096                                           *:9323                                        *:*                                      
LISTEN              0                    4096                                        [::]:5355                                     [::]:*                                      
LISTEN              0                    4096                                           *:9100                                        *:*                                      
```

## Why ifconfig and netstat where deprecated?

In this case it [was lack of maintenance](https://lists.debian.org/debian-devel/2009/03/msg00780.html). So newer tools took its place:


> Many Linux distributions have deprecated the use of ifconfig and route in favor of the software suite iproute2, such as ArchLinux[3] or RHEL since version 7,[4] which has been available since 1999 for Linux 2.2.[5] iproute2 includes support for all common functions of ifconfig(8), route(8), arp(8) and netstat(1). It also includes multicast configuration support, tunnel and virtual link management, traffic control, and low-level IPsec configuration, among other features.


# What did we learn so far

* It is a good idea to keep up with the latest tools, as developers fix bugs and add useful functionality that may not be present with older versions. It is all about being more productive.
* Old software tend not to get bug-fixes. Some of them [could compromise your system](https://nvd.nist.gov/vuln/detail/CVE-2022-28391) if left unattended.
* And not every claim that a tool is deprecated is true! as usual, do your homework and make sure your tools are up-to-date.

