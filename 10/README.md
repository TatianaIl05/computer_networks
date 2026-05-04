Выполнить DNS-запрос для домена и сохранить IP-адреса в $googleIPs.
```
$googleIPs = (Resolve-DnsName google.com -Type A).IPAddress
$googleIPs
```
Выполнить traceroute для IP-адреса в качестве примера.
```
$targetIP = $googleIPs[0]
tracert -d $targetIP
```
или для Linux:
```
googleIPs=($(dig +short google.com | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'))
printf '%s\n' "${googleIPs[@]}"
```
```
targetIP=${googleIPs[0]}
traceroute -n $targetIP
```

Пример вывода:

  1     2 ms     2 ms    51 ms  172.20.10.1 
  
  2     *        *        *     Превышен интервал ожидания для запроса.
  
  3     *        *        *     Превышен интервал ожидания для запроса.
  
 10   113 ms   101 ms   100 ms  178.176.152.61 
 
 11   119 ms   101 ms    94 ms  192.178.241.251 
 
 12   105 ms   101 ms   100 ms  192.178.241.234 
 
 13   105 ms     *        *     142.250.238.138 
 
 14   120 ms    85 ms    79 ms  142.250.235.68 
 
 15    93 ms    94 ms   101 ms  142.250.210.47 
 
 16     *        *        *     Превышен интервал ожидания для запроса.
 
 25     *        *        *     Превышен интервал ожидания для запроса.
 
 26   139 ms   101 ms    99 ms  142.251.1.138 
