#!/bin/bash

docker network create \
  --driver bridge \
  --ipv6 \
  --subnet=172.26.0.0/16 \
  --subnet=2001:db8:3::/64 \
  dual-network

docker run -d --name container1 --network dual-network alpine sleep 3600
docker run -d --name container2 --network dual-network alpine sleep 3600

docker exec container1 apk add tcpdump
docker exec container2 apk add tcpdump

IPV4=$(docker exec container2 ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
IPV6=$(docker exec container2 ip -6 addr show eth0 | grep -oP '(?<=inet6\s)[a-f0-9:]+' | grep -v fe80 | head -1)

docker exec container1 tcpdump -i eth0 -c 5 -n ip -w /tmp/ipv4.pcap 2>/dev/null & sleep 1
docker exec container1 ping -c 3 $IPV4

sleep 2

echo "ЗАХВАЧЕННЫЕ IPv4 ПАКЕТЫ:"
docker exec container1 tcpdump -r /tmp/ipv4.pcap -n 2>/dev/null

docker exec container1 tcpdump -i eth0 -c 5 -n ip6 -w /tmp/ipv6.pcap 2>/dev/null & sleep 1
docker exec container1 ping6 -c 3 $IPV6

sleep 2

echo "ЗАХВАЧЕННЫЕ IPv6 ПАКЕТЫ:"
docker exec container1 tcpdump -r /tmp/ipv6.pcap -n 2>/dev/null

docker exec container1 tcpdump -i eth0 -c 4 -n icmp6 -w /tmp/ndp.pcap 2>/dev/null & sleep 1
docker exec container1 ping6 -c 2 $IPV6
sleep 2

docker stop container1 container2
docker rm container1 container2
docker network rm dual-network
